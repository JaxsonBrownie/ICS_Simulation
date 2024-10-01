#!/usr/bin/env python3

import time
import logging
import sys
import constants
import argparse
from flask_cors import CORS
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
CORS(app)

###########################################################
# Function: plc1_client
# Purpose: Handles the Modbus TCP client for reading from
#    PLC 1
###########################################################
def plc1_client(client : ModbusClient):
    global plc1_holding_regs, plc1_coils, plc1_lock

    # polling loop
    while True:
        reg_list = client.read_holding_registers(20, 2)
        coil_list = client.read_coils(10, 1)

        # store recorded values
        if reg_list:
            with plc1_lock:
                plc1_holding_regs = list(reg_list)

        if coil_list:
            with plc1_lock:
                plc1_coils = list(coil_list)

        # delay between polls
        time.sleep(constants.HMI_POLL_SPEED)

###########################################################
# Function: plc2_client
# Purpose: Handles the Modbus TCP client for reading from
#    PLC 2
###########################################################
def plc2_client(client : ModbusClient):
    global plc2_holding_regs, plc2_coils, plc2_lock

    # polling loop
    while True:
        reg_list = client.read_holding_registers(20, 2)
        coil_list = client.read_coils(10, 1)

        # store recorded values
        if reg_list:
            with plc2_lock:
                plc2_holding_regs = list(reg_list)

        if coil_list:
            with plc2_lock:
                plc2_coils = list(coil_list)

        # delay between polls
        time.sleep(constants.HMI_POLL_SPEED)

###########################################################
# Wrapped Function: index
# Purpose: Simple endpoint for the Flask server
###########################################################
@app.route('/')
def index():
    global plc1_holding_regs, plc1_coils, plc2_holding_regs, plc2_coils
    return jsonify(
        {
            "plc1" : 
            {
                "hr" : plc1_holding_regs, 
                "coil" : plc1_coils
            },
            "plc2" :
            {
                "hr" : plc2_holding_regs, 
                "coil" : plc2_coils
            }
        })


###########################################################
# Special Function: __main__
# Purpose: Sets up the two Modbus TCP clients for the 2 PLCs.
#   Each client runs as their own thread. Finally, sets up
#   the Flask server endpoints.
###########################################################
if __name__ == '__main__':
    # pass args
    parser = argparse.ArgumentParser(description="Human Machine Interface")
    
    # Add arguments
    parser.add_argument('-1', '--plc1', type=str, help='IP of PLC 1')
    parser.add_argument('-2', '--plc2', type=str, help='IP of PLC 2')
    parser.add_argument('-P', '--webport', type=str, help='The port number for the web server')

    # Parse the arguments
    args = parser.parse_args()
    client1_ip = args.plc1
    client2_ip = args.plc2
    webport = args.webport

    # init modbus PLC1 client
    client1 = ModbusClient(host=client1_ip, port=502, unit_id=1)

    # start the PLC1 client thread
    _logger.info(f"Starting PLC1 HMI Client: {client1_ip}")
    tp = Thread(target=plc1_client, args=(client1,))
    tp.daemon = True # to kill the thread when the main thread exits
    tp.start()

    # init modbus PLC2 client
    client2 = ModbusClient(host=client2_ip, port=502, unit_id=1)

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
    app.run(host="0.0.0.0", port=webport)