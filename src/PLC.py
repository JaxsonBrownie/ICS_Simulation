#!/usr/bin/env python3

import logging
import sys
import time
from dataset import AusgridDataset
from enum import Enum
from threading import Thread, Lock
from pyModbusTCP.server import ModbusServer, DataBank
from pyModbusTCP.client import ModbusClient
from pymodbus.client import ModbusSerialClient

# enum to represent the switch state
class TRANSFER_SWITCH(Enum):
    SOLAR = True
    MAINS = False

# set global variables
lock = Lock()

# create logger
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
_logger.addHandler(console_handler)

################################################################################

"""Reads in solar panel readings from the provided dataset"""
def _get_ats_threshold(filename):
    # create dataset object for the Ausgrid dataset
    dataset = AusgridDataset()

    # read in the dataset csv file
    dataset.readFile(filename)

    # extract the required values from the dataset
    values = dataset.extract()
    switching_threshold = (values[2]/24)*0.3

    return switching_threshold

################################################################################

"""Thread for the PLC server"""
def plc_server(server : ModbusServer):
    server.start()

################################################################################

"""Thread for the PLC client to the power meter"""
def plc_client_power_meter(client : ModbusSerialClient, data_bank : DataBank):
    while True:
        # read the power meter input register
        pm_value = client.read_input_registers(20, 1, unit=1)
        if not pm_value.isError():
            # write the Modbus RTU power meter input to the Modbus TCP server memory (same address)
            #_logger.info(f'Power Meter: {pm_value.registers} °C')
            data_bank.set_input_registers(20, pm_value.registers)

        time.sleep(0.1)

################################################################################

"""Thread for the PLC client to the transfer switch"""
def plc_client_transfer_switch(client : ModbusSerialClient, data_bank : DataBank, switching_threshold):
    switch_value = TRANSFER_SWITCH.MAINS

    while True:
        # read the power meter input register from Modbus TCP server data bank
        pm_value = data_bank.get_input_registers(20, 1)

        # set the coil on the transfer switch depending on power output
        if pm_value:
            if pm_value[0] < switching_threshold:
                switch_value = TRANSFER_SWITCH.MAINS
            else:
                switch_value = TRANSFER_SWITCH.SOLAR
        client.write_coil(10, switch_value.value)
        #_logger.info(f'Transfer Switch: {switch_value.value}')

        # write coil transfer switch value to plc's server memory (same address)
        data_bank.set_coils(10, [switch_value.value])

        time.sleep(0.1)

################################################################################

if __name__ == '__main__':
    # verify args
    if len(sys.argv) < 3:
        print("Incorrect number of arguments")
        exit(1)
    
    server_ip = "0.0.0.0"
    server_port = 5020

    client1_com = sys.argv[1]
    client2_com = sys.argv[2]

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
    # init modbus server
    data_bank = DataBank()
    server = ModbusServer(host=server_ip, port=server_port, data_bank=data_bank, no_block=True)

    # start the PLC server thread
    _logger.info(f"Starting PLC Server")
    tp_server = Thread(target=plc_server, args=(server,))
    tp_server.daemon = True
    tp_server.start()

    #----------------------------------------------------------------------
    # init power meter modbus client
    pm_client = ModbusSerialClient(port=client1_com, baudrate=9600, timeout=1)
    pm_client.connect()

    # start the power meter client thread
    _logger.info(f"Starting PLC Power Meter Client")
    tp_client = Thread(target=plc_client_power_meter, args=(pm_client, data_bank))
    tp_client.daemon = True
    tp_client.start()

    #----------------------------------------------------------------------
    # init transfer switch modbus client
    ts_client = ModbusSerialClient(port=client2_com, baudrate=9600, timeout=1)
    ts_client.connect()

    # start the transfer switch client thread
    _logger.info(f"Starting PLC Transfer Switch Client")
    switching_threshold = _get_ats_threshold("solar-home-data.csv")
    
    _logger.info(f"ATS threshold value: {switching_threshold}")
    tp_client = Thread(target=plc_client_transfer_switch, args=(ts_client, data_bank, switching_threshold))
    tp_client.daemon = True
    tp_client.start()

    while True:        
        time.sleep(1)

################################################################################