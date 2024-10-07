#!/usr/bin/env python3

import logging
import sys
import time
import constants
import argparse
import subprocess
from dataset import AusgridDataset
from enum import Enum
from threading import Thread, Lock
from pyModbusTCP.server import ModbusServer, DataBank, DeviceIdentification, DataHandler
from pymodbus.client import ModbusSerialClient
from threading import Event, Lock, Thread
from pyModbusTCP.constants import (ENCAPSULATED_INTERFACE_TRANSPORT, EXP_DATA_ADDRESS,
                        EXP_DATA_VALUE, EXP_ILLEGAL_FUNCTION, EXP_NONE,
                        MAX_PDU_SIZE, MEI_TYPE_READ_DEVICE_ID, READ_COILS,
                        READ_DISCRETE_INPUTS, READ_HOLDING_REGISTERS,
                        READ_INPUT_REGISTERS, WRITE_MULTIPLE_COILS,
                        WRITE_MULTIPLE_REGISTERS,
                        WRITE_READ_MULTIPLE_REGISTERS, WRITE_SINGLE_COIL,
                        WRITE_SINGLE_REGISTER)

# enum to represent the switch state
class TRANSFER_SWITCH(Enum):
    SOLAR = True
    MAINS = False

# set global variables
lock = Lock()
restartPLC = False

# create logger
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
_logger.addHandler(console_handler)
   

###########################################################
# Class: CustomModbusServer(ModbusServer)
# Purpose: Extends the ModbusServer class to add a custom
#   external engine and function codes. Implements 0x08
#   diagnostic function.
###########################################################
class CustomModbusServer(ModbusServer):
    
    def __init__(self, host='localhost', port=502, no_block=False, ipv6=False,
                 data_bank=None, data_hdl=None, ext_engine=None, device_id=None):
        super().__init__(host, port, no_block, ipv6, data_bank, data_hdl, ext_engine, device_id)

        # custom fields
        self._force_listen_only = False
    
        # modbus default functions map + custom functions
        self._func_map = {READ_COILS: self._read_bits,
                        READ_DISCRETE_INPUTS: self._read_bits,
                        READ_HOLDING_REGISTERS: self._read_words,
                        READ_INPUT_REGISTERS: self._read_words,
                        WRITE_SINGLE_COIL: self._write_single_coil,
                        WRITE_SINGLE_REGISTER: self._write_single_register,
                        WRITE_MULTIPLE_COILS: self._write_multiple_coils,
                        WRITE_MULTIPLE_REGISTERS: self._write_multiple_registers,
                        WRITE_READ_MULTIPLE_REGISTERS: self._write_read_multiple_registers,
                        ENCAPSULATED_INTERFACE_TRANSPORT: self._encapsulated_interface_transport,
                        0x08: self._diagnostics}
        
    def set_force_listen_only(self, value):
        self._force_listen_only = value

    def get_force_listen_only(self):
        return self._force_listen_only

    def custom_engine(self, session_data):
        """Default internal processing engine: call default modbus func.

        :type session_data: ModbusServer.SessionData
        """
        try:
            # call the ad-hoc function, if none exists, send an "illegal function" exception
            func = self._func_map[session_data.request.pdu.func_code]

            # check function found is callable
            if not callable(func):
                raise TypeError
            
            # check if device is not in force listen only mode
            if not self._force_listen_only:
                # call ad-hoc func
                func(session_data)
        except (TypeError, KeyError):
            session_data.response.pdu.build_except(session_data.request.pdu.func_code, EXP_ILLEGAL_FUNCTION)

    def _diagnostics(self, session_data):
        """
        Function Diagnostics (0x08)

        :param session_data: server engine data
        :type session_data: ModbusServer.SessionData
        """
        # global variables
        global restartPLC

        # pdu alias
        recv_pdu = session_data.request.pdu
        send_pdu = session_data.response.pdu
        # decode pdu
        (sub_fc, bits) = recv_pdu.unpack('>HH', from_byte=1, to_byte=5)
        # handle sub-function codes
        if sub_fc == 0x0004:    # Force Listen Only Mode
            self._force_listen_only = True
        elif sub_fc == 0x0001:  # Restart Communications
            restartPLC = True

        # send back reflected packet
        send_pdu.add_pack('>BHH', recv_pdu.func_code, sub_fc, bits)

###########################################################
# Private Function: get_ats_threshold
# Purpose: Creates an AusgridDataset object to read in the
#   dataset and to extract the required data for calculating
#   the switching threshold for the transfer switch
###########################################################
def _get_ats_threshold(filename):
    # create dataset object for the Ausgrid dataset
    dataset = AusgridDataset()

    # read in the dataset csv file
    dataset.readFile(filename)

    # extract the required values from the dataset
    values = dataset.extract()

    # calculate the ATS switching threshold
    # this threshold is 20% of the average energy consumption price for the month
    switching_threshold = (values[2]/24)*0.2

    return switching_threshold

###########################################################
# Function: plc_server
# Purpose: Starts the Modbus TCP server in a separate thread
###########################################################
def plc_server(server : ModbusServer):
    server.start()

###########################################################
# Function: plc_client_power_meter
# Purpose: Sets up the Modbus RTU client to read values from
#   the solar panel. The values are then written to the PLCs
#   Modbus TCP server data bank.
###########################################################
def plc_client_power_meter(client : ModbusSerialClient, data_bank : DataBank, slave_id):
    global restartPLC
    while True:
        if restartPLC == False:
            # read the power meter holding register
            pm_value = client.read_holding_registers(20, 1, slave=slave_id)
            if not pm_value.isError():
                # write the Modbus RTU power meter input to the Modbus TCP server memory (same address)
                _logger.debug(f'Power Meter: {pm_value.registers} °C')
                data_bank.set_holding_registers(20, pm_value.registers)

            time.sleep(constants.PM_POLL_SPEED)

###########################################################
# Function: plc_client_transfer_switch
# Purpose: Sets up the Modbus RTU client to write to the
#   transfer switch. This client handles the transfer switch
#   logic: It reads the solar panel reading from the Modbus
#   TCP databank, checks if it is under or over the switching
#   threshold, then write to the transfer switch to either
#   switch the mains power or solar power.
###########################################################
def plc_client_transfer_switch(client : ModbusSerialClient, data_bank : DataBank, slave_id, switching_threshold):
    global restartPLC
    switch_value = TRANSFER_SWITCH.MAINS

    # write the switching threshold to holding register 21 of the TCP server
    data_bank.set_holding_registers(21, [switching_threshold])

    while True:
        if restartPLC == False:
            # read the power meter holding register from Modbus TCP server data bank
            pm_value = data_bank.get_holding_registers(20, 1)

            # set the coil on the transfer switch depending on power output
            if pm_value:
                if pm_value[0] <= switching_threshold:
                    switch_value = TRANSFER_SWITCH.MAINS
                else:
                    switch_value = TRANSFER_SWITCH.SOLAR
            client.write_coil(10, switch_value.value, slave=slave_id)
            #_logger.info(f'Transfer Switch: {switch_value.value}')

            # write coil transfer switch value to plc's server memory (same address)
            data_bank.set_coils(10, [switch_value.value])

            time.sleep(constants.TS_POLL_SPEED)

###########################################################
# Special Function: __main__
# Purpose: Sets up the two Modbus RTU clients and the Modbus
#   TCP server.
###########################################################
if __name__ == '__main__':
    # pass args
    parser = argparse.ArgumentParser(description="Programmable Logic Controller")
    
    # Add arguments
    parser.add_argument('-c', '--comm', type=str, help='Comm port for the serial Modbus client connection')
    parser.add_argument('-s1', '--pm_slave', type=int, help='Modbus RTU slave id for the power meter')
    parser.add_argument('-s2', '--ts_slave', type=int, help='Modbus RTU slave id for the transfer switch')

    # Parse the arguments
    args = parser.parse_args()
    comm = args.comm
    pm_slave_id = args.pm_slave
    ts_slave_id = args.ts_slave
    
    server_ip = "0.0.0.0"
    server_port = 502

    # (ASCII font "Big" https://patorjk.com/software/taag/#p=display&f=Big)
    title = """
        ---------------------
         _____  _      _____  
        |  __ \| |    / ____|
        | |__) | |   | |     
        |  ___/| |   | |     
        | |    | |___| |____ 
        |_|    |______\_____|
        ---------------------
        """
    print(title)

    #----------------------------------------------------------------------
    # init Modbus TCP server data bank
    data_bank = DataBank()

    # create device identification
    vendor_name = "Curtin University".encode("utf-8")
    product_code = "X7K8P2Z4W9".encode("utf-8")
    major_minor_revision = "1.3.0".encode("utf-8")
    vendor_url = "https://www.curtin.edu.au/".encode("utf-8")
    product_name = "Smart Grid PLC".encode("utf-8")
    model_name = "PLCv1.3.0".encode("utf-8")
    user_app_name = "Smart Grid PLC".encode("utf-8")

    device_id = DeviceIdentification(
        vendor_name=vendor_name,
        product_code=product_code,
        major_minor_revision=major_minor_revision,
        vendor_url=vendor_url,
        product_name=product_name,
        model_name=model_name,
        user_application_name=user_app_name
        )

    server = CustomModbusServer(host=server_ip, port=server_port, no_block=True, device_id=device_id, data_bank=data_bank)
    server.ext_engine = server.custom_engine

    # start the PLC server thread
    _logger.info(f"Starting PLC Server")
    tp_server = Thread(target=plc_server, args=(server,))
    tp_server.daemon = True
    tp_server.start()

    #----------------------------------------------------------------------
    # init Modbus RTU client
    client = ModbusSerialClient(port=comm, baudrate=9600, timeout=1)
    client.connect()

    # start the power meter client thread
    _logger.info(f"Starting PLC Power Meter Client")
    tp_client = Thread(target=plc_client_power_meter, args=(client, data_bank, pm_slave_id))
    tp_client.daemon = True
    tp_client.start()

    # get transfer switch switching threshol
    _logger.info(f"Starting PLC Transfer Switch Client")
    switching_threshold = int(_get_ats_threshold("solar-home-data.csv"))

    # start the transfer switch client thread    
    _logger.info(f"ATS threshold value: {switching_threshold}")
    tp_client = Thread(target=plc_client_transfer_switch, args=(client, data_bank, ts_slave_id, switching_threshold))
    tp_client.daemon = True
    tp_client.start()


    # process loop
    while True:        
        time.sleep(1)

        # simulate the PLC restarting
        if restartPLC:
            _logger.warning("Restarting PLC")
            time.sleep(10)
            restartPLC = False