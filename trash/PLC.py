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

"""Thread for the PLC server"""
def plc_server(server : ModbusServer):
    server.start()

################################################################################

"""Thread for the PLC client to the power meter"""
def plc_client_power_meter(client : ModbusClient, data_bank : DataBank):
    while True:
        # read the power meter input register
        pm_value = client.read_input_registers(20, 1)

        # write the power meter input to the plc's server memory (same address)
        if pm_value:
            data_bank.set_input_registers(20, pm_value)

        time.sleep(2)

################################################################################

"""Thread for the PLC client to the transfer switch"""
def plc_client_transfer_switch(client : ModbusClient, data_bank : DataBank):
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

    # init modbus server
    data_bank = DataBank()
    server = ModbusServer(host=server_ip, port=server_port, data_bank=data_bank, no_block=True)

    # start the PLC server thread
    _logger.info(f"Starting PLC1 Server")
    tp_server = Thread(target=plc_server, args=(server,))
    tp_server.daemon = True
    tp_server.start()

    # init power meter modbus client
    client1 = ModbusClient(host=client1_ip, port=client_port, unit_id=1)

    # start the power meter client thread
    _logger.info(f"Starting PLC Power Meter Client")
    tp_client = Thread(target=plc_client_power_meter, args=(client1, data_bank))
    tp_client.daemon = True
    tp_client.start()

    # init transfer switch modbus client
    client2 = ModbusClient(host=client2_ip, port=client_port, unit_id=1)

    # start the transfer switch client thread
    _logger.info(f"Starting PLC Transfer Switch Client")
    tp_client = Thread(target=plc_client_transfer_switch, args=(client2, data_bank))
    tp_client.daemon = True
    tp_client.start()


    while True:        
        time.sleep(1)

################################################################################