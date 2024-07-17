#!/usr/bin/env python3

import time
import logging
import sys
import os
from threading import Thread, Lock
from pyModbusTCP.client import ModbusClient

# set global variables
plc1_holding_regs = [0]
plc1_coils = [False]
plc1_lock = Lock()

plc2_holding_regs = [0]
plc2_coils = [False]
plc2_lock = Lock()

# create logger
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
_logger.addHandler(console_handler)

################################################################################

"""PLC1 HMI client thread"""
def plc1_client(client : ModbusClient):
    global plc1_holding_regs, plc1_coils, plc1_lock

    # polling loop
    while True:
        reg_list = client.read_holding_registers(10, 20)
        coil_list = client.read_coils(10, 1)

        # store recorded values
        if reg_list:
            with plc1_lock:
                plc1_holding_regs = list(reg_list)

        if coil_list:
            with plc1_lock:
                plc1_coils = list(coil_list)

        # delay between polls
        time.sleep(0.5)

################################################################################

if __name__ == '__main__':

    # init modbus PLC1 client
    client1 = ModbusClient(host="127.0.0.1", port=5020, unit_id=1)

    # start the PLC1 client thread
    _logger.info("Starting PLC1 HMI Client")
    tp = Thread(target=plc1_client, args=(client1,))
    tp.daemon = True # to kill the thread when the main thread exits
    tp.start()
    
    # (ASCII font "Big" https://patorjk.com/software/taag/#p=display&f=Big)
    title = """
        TEST HMI to TCP Server -> RTU Slave
        """
    
    while True:
        _logger.info(f"HR: {plc1_holding_regs}")

        time.sleep(1)