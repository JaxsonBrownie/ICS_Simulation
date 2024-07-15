#!/usr/bin/env python3

import time
import logging
import sys
from enum import Enum
from threading import Thread, Lock
from pyModbusTCP.client import ModbusClient
from pyModbusTCP.server import ModbusServer, DataBank

# set global variables
#lock = Lock()

# enum to represent the switch state
class TRANSFER_SWITCH(Enum):
    SOLAR = True
    MAINS = False

# create logger
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
_logger.addHandler(console_handler)

################################################################################

"""Thread to simulate the transfer switch actuator"""
def transfer_switch(server : ModbusServer, data_bank : DataBank):
    server.start()

    switch_value = TRANSFER_SWITCH.MAINS

    while True:
        # read the switch coil
        switch_coil = data_bank.get_coils(10, 1)

        # set the constant
        if switch_coil:
            if switch_coil[0]:
                switch_value = TRANSFER_SWITCH.SOLAR
            else:
                switch_value = TRANSFER_SWITCH.MAINS
            _logger.info(f"TRANSFER SWITCH COIL: {switch_coil[0]}")
        _logger.info(f"TRANSFER SWITCH: {switch_value}")

        time.sleep(2)

################################################################################

if __name__ == '__main__':
    server_ip = "0.0.0.0"
    server_port = 5020

    # init modbus server
    data_bank = DataBank()
    server = ModbusServer(host=server_ip, port=server_port, data_bank=data_bank, no_block=True)

    # start the server thread
    tp_server = Thread(target=transfer_switch, args=(server, data_bank))
    tp_server.daemon = True
    tp_server.start()

    _logger.info("Starting Transfer Switch")
    
    # (ASCII font "Big" https://patorjk.com/software/taag/#p=display&f=Big)
    title = """
        ---------------------------
        <todo>
        ---------------------------
        """
    print(title)

    while True:
        time.sleep(1)