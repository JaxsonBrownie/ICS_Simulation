#!/usr/bin/env python3
import time
import logging
import sys
import os
from flask import Flask, jsonify
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

# create flask app
app = Flask(__name__)

################################################################################

"""PLC1 HMI client thread"""
def plc1_client(client : ModbusClient):
    global plc1_holding_regs, plc1_coils, plc1_lock

    # polling loop
    while True:
        reg_list = client.read_input_registers(20, 1)
        coil_list = client.read_coils(10, 1)

        # store recorded values
        if reg_list:
            with plc1_lock:
                plc1_holding_regs = list(reg_list)

        if coil_list:
            with plc1_lock:
                plc1_coils = list(coil_list)

        # delay between polls
        time.sleep(0.2)

################################################################################

"""PLC2 HMI client thread"""
def plc2_client(client : ModbusClient):
    global plc2_holding_regs, plc2_coils, plc2_lock

    # polling loop
    while True:
        reg_list = client.read_input_registers(20, 1)
        coil_list = client.read_coils(10, 1)

        # store recorded values
        if reg_list:
            with plc2_lock:
                plc2_holding_regs = list(reg_list)

        if coil_list:
            with plc2_lock:
                plc2_coils = list(coil_list)

        # delay between polls
        time.sleep(0.2)

################################################################################

"""Flask web server"""
@app.route('/')
def index():
    global plc1_holding_regs, plc1_coils, plc2_holding_regs, plc2_coils
    return jsonify(
        {
            "plc1" : 
            {
                "hr" : plc1_holding_regs, 
                "co" : plc1_coils
            },
            "plc2" :
            {
                "hr" : plc2_holding_regs, 
                "co" : plc2_coils
            }
        })

################################################################################

if __name__ == '__main__':
    # verify args
    if len(sys.argv) < 3:
        print("Incorrect number of arguments")
        exit(1)
    
    client1_ip = sys.argv[1]
    client2_ip = sys.argv[2]

    # init modbus PLC1 client
    client1 = ModbusClient(host=client1_ip, port=5020, unit_id=1)

    # start the PLC1 client thread
    _logger.info(f"Starting PLC1 HMI Client: {client1_ip}")
    tp = Thread(target=plc1_client, args=(client1,))
    tp.daemon = True # to kill the thread when the main thread exits
    tp.start()

    # init modbus PLC2 client
    client2 = ModbusClient(host=client2_ip, port=5020, unit_id=1)

    # start the PLC2 client thread
    _logger.info(f"Starting PLC2 HMI Client: {client2_ip}")
    tp = Thread(target=plc2_client, args=(client2,))
    tp.daemon = True # to kill the thread when the main thread exits
    tp.start()
    
    # (ASCII font "Big" https://patorjk.com/software/taag/#p=display&f=Big)
    title = """
        ---------------------
         _    _ __  __ _____ 
        | |  | |  \/  |_   _|
        | |__| | \  / | | |  
        |  __  | |\/| | | |  
        | |  | | |  | |_| |_ 
        |_|  |_|_|  |_|_____|
        ---------------------
        """
    print(title)

    # start flask web server (without terminal logs)
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR) 
    app.run(host="0.0.0.0", port=8000)

    #while True:
    #    _logger.info(f"PLC1 Solar Panel Power Meter (mW): {plc1_holding_regs[0]}")
    #    _logger.info(f"PLC1 Transfer Switch (Mains/Solar): {plc1_coils[0]}")
    #    _logger.info(f"PLC2 Solar Panel Power Meter (mW): {plc2_holding_regs[0]}")
    #    _logger.info(f"PLC2 Transfer Switch (Mains/Solar): {plc2_coils[0]}")

    #    time.sleep(0.2)