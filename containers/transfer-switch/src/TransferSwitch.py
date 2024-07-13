#!/usr/bin/env python3

import time
import logging
import sys
import os
import numpy as np
from enum import Enum
from scipy.stats import norm
from threading import Thread, Lock
from pyModbusTCP.client import ModbusClient

# set global variables
lock = Lock()

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

"""Thread to simulate the transfer switch"""
def transfer_switch(client : ModbusClient):
    global lock
    switch_value = TRANSFER_SWITCH.MAINS
    power_output = 0

    while True:
        # read the switch coil
        switch_coil = client.read_coils(10, 1)

        # set the constant
        if switch_coil:
            with lock:
                if switch_coil[0]:
                    switch_value = TRANSFER_SWITCH.SOLAR
                else:
                    switch_value = TRANSFER_SWITCH.MAINS
        _logger.info(f"TRANSFER SWITCH: {switch_value}")

        # simulate the power switch
        if switch_value == TRANSFER_SWITCH.MAINS:
            power_output = 833
        else:
            power_output = client.read_holding_registers(20, 1)[0]
        _logger.info(f"TRANSFER SWITCH POWER: {power_output} mW")

        time.sleep(2)

################################################################################

if __name__ == '__main__':
    # init modbus client
    client = ModbusClient(host="127.0.0.1", port=5020, unit_id=1)

    # start the HIL client thread
    tp = Thread(target=transfer_switch, args=(client,))
    tp.daemon = True # to kill the thread when the main thread exits
    tp.start()

    _logger.info("Starting HMI Client")
    
    # (ASCII font "Big" https://patorjk.com/software/taag/#p=display&f=Big)
    title = """
        ---------------------------
        <todo>
        ---------------------------
        """
    print(title)

    while True:
        time.sleep(1)