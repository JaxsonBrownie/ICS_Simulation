#!/usr/bin/env python3

import time
import logging
import sys
import os
from threading import Thread, Lock
from pyModbusTCP.client import ModbusClient

# set global variables
holding_regs = []
coils = []
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

"""A simple thread to simulate a HMI"""
def hardware_in_loop(client : ModbusClient):
    global holding_regs, coils, lock

    # polling loop
    while True:
        coil_list = client.read_coils(10, 1)
        reg_list = client.read_holding_registers(20, 1)

        # store recorded values
        if reg_list:
            with lock:
                holding_regs = list(reg_list)

        if coil_list:
            with lock:
                coils = list(coil_list)

        # delay between polls
        time.sleep(0.5)

################################################################################

if __name__ == '__main__':
    # init modbus client
    client = ModbusClient(host="127.0.0.1", port=5020, unit_id=1)

    # start the HIL client thread
    tp = Thread(target=hardware_in_loop, args=(client,))
    tp.daemon = True # to kill the thread when the main thread exits
    tp.start()

    _logger.info("Starting HMI Client")
    
    # (ASCII font "Big" https://patorjk.com/software/taag/#p=display&f=Big)
    title = """
        ---------------------------
         _    _ __  __ _____ __ 
        | |  | |  \/  |_   _/_ |
        | |__| | \  / | | |  | |
        |  __  | |\/| | | |  | |
        | |  | | |  | |_| |_ | |
        |_|  |_|_|  |_|_____||_|
        ---------------------------
        """
    while True:
        # clear terminal
        os.system('clear')
        print(title)

        with lock:
            print("=============================================================")
            print(f"Current reading from the solar panel power meter (mW): {holding_regs[0]}")
            if coils[0]:
                print("Power supply input: Solar Panels")
            else:
                print("Power supply input: Mains Power")
            print("=============================================================")
            print()
            print()
            print()
            print()
            print()
            print()
            print()
            print("----------------------------")
            print("| Raw Modbus Input:")
            print(f"| holding registers: {holding_regs}")
            print(f"| coils: {coils}")
            print("----------------------------")

        time.sleep(0.5)