#!/usr/bin/env python3

""" Read 10 coils and print result on stdout. """

import time
import logging
import sys
from threading import Thread, Lock
from pyModbusTCP.client import ModbusClient

# set global variables
holding_regs = []
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

"""Sets up the client with attributes"""
def setup_client():
    client_attributes = {}
    
    client_attributes["target_ip"] = "127.0.0.1"
    client_attributes["port"] = 5020
    client_attributes["unit_id"] = 1

    return client_attributes

################################################################################

"""A simple thread to simulate a HIL"""
def hardware_in_loop(attributes):
    global holding_regs, lock

    # init modbus client
    client = ModbusClient(host=attributes["target_ip"], port=attributes["port"], unit_id=attributes["unit_id"])

    # polling loop
    while True:
        reg_list = client.read_holding_registers(0, 10)

        # if read is ok, store result in global var (with thread lock)
        if reg_list:
            with lock:
                holding_regs = list(reg_list)
        time.sleep(1)

################################################################################

if __name__ == '__main__':
    # setup the client
    client_attributes = setup_client()

    # start the HIL client thread
    tp = Thread(target=hardware_in_loop, args=(client_attributes,))
    tp.daemon = True # to kill the thread when the main thread exits
    tp.start()

    while True:
        with lock:
            print(holding_regs)

        time.sleep(1)