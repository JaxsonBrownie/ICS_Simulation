#!/usr/bin/env python3

import logging
import sys
import time
from enum import Enum
from threading import Thread, Lock
from pyModbusTCP.server import ModbusServer, DataBank
from pyModbusTCP.client import ModbusClient

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

"""
Inherited Class: DataBankLogic
Purpose: A custom ModbusServerDataBank to control logic within the PLC
"""
#class DataBankLogic(DataBank):
#    """
#    Overrided Function: on_holding_registers_change
#    Purpose: Defines logic to be executed when a holding register value changes
#    """
#    def on_holding_registers_change(self, address, from_value, to_value, srv_info):
#        # control the transfer switch
#        if address == 20:
#            self.__transfer_switch_logic(to_value, 800)
#
#    """
#    Private Function: transfer_switch_logic
#    Purpose: Simulates the transfer swtich logic
#    """
#    def __transfer_switch_logic(self, power, power_thresh, switch_addr):
#        # check whether need to switch to mains (0) or keep solar (1)
#        if power < power_thresh:
#            # switch to mains
#            pass
#            #self.set_coils(switch_addr, [False])
#        else:
#            # switch to solar power
#            pass
#            #self.set_coils(switch_addr, [True])


################################################################################

"""Thread for the PLC server"""
def plc_server(server : ModbusServer):
    _logger.info(f"Starting PLC1 Server")
    server.start()

################################################################################

"""Thread for the PLC client to the power meter"""
def plc_client_power_meter(client : ModbusClient, data_bank : DataBank):
    _logger.info(f"Starting PLC1 Power Meter Client")

    while True:
        # read the power meter input register
        pm_value = client.read_input_registers(20, 1)

        # write the power meter input to the plc's server memory (same address)
        if pm_value:
            data_bank.set_input_registers(20, pm_value)
            _logger.info(f"SOLAR PANEL POWER METER: {data_bank.get_input_registers(20, 1)}")

        time.sleep(2)

################################################################################

"""Thread for the PLC client to the transfer switch"""
def plc_client_transfer_switch(client : ModbusClient, data_bank : DataBank):
    _logger.info(f"Starting PLC1 Transfer Switch Client")
    switch_value = TRANSFER_SWITCH.MAINS

    while True:
        # read the power meter input register from data bank
        pm_value = data_bank.get_input_registers(20, 1)

        # set the coil on the transfer switch depending on power output
        if pm_value:
            if pm_value[0] < 100:
                switch_value = TRANSFER_SWITCH.MAINS
            else:
                switch_value = TRANSFER_SWITCH.SOLAR
        client.write_single_coil(10, switch_value.value)
        _logger.info(f"TRANSFER SWITCH VALUE: {switch_value.value}")

        # write coil transfer switch value to plc's server memory (same address)
        data_bank.set_coils(10, [switch_value.value])

        time.sleep(1)

################################################################################

if __name__ == '__main__':
    # verify args
    if len(sys.argv) < 3:
        print("Incorrect number of arguments")
        exit(1)
    
    server_ip = "0.0.0.0"
    server_port = 5020

    client1_ip = sys.argv[1]
    client2_ip = sys.argv[2]
    client_port = 5020

    # (ASCII font "Big" https://patorjk.com/software/taag/#p=display&f=Big)
    title = """
        -------------------------
         _____  _      _____ __ 
        |  __ \| |    / ____/_ |
        | |__) | |   | |     | |
        |  ___/| |   | |     | |
        | |    | |___| |____ | |
        |_|    |______\_____||_|
        -------------------------
        """
    print(title)

    # init modbus server
    data_bank = DataBank()
    server = ModbusServer(host=server_ip, port=server_port, data_bank=data_bank, no_block=True)

    # start the PLC server thread
    tp_server = Thread(target=plc_server, args=(server,))
    tp_server.daemon = True
    tp_server.start()

    # init power meter modbus client
    client1 = ModbusClient(host=client1_ip, port=client_port, unit_id=1)

    # start the power meter client thread
    tp_client = Thread(target=plc_client_power_meter, args=(client1, data_bank))
    tp_client.daemon = True
    tp_client.start()

    # init transfer switch modbus client
    client2 = ModbusClient(host=client2_ip, port=client_port, unit_id=1)

    # start the transfer switch client thread
    tp_client = Thread(target=plc_client_transfer_switch, args=(client2, data_bank))
    tp_client.daemon = True
    tp_client.start()


    while True:        
        time.sleep(1)

################################################################################