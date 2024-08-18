#!/usr/bin/env python3

import time
import logging
import sys
import constants
import argparse
from flask_cors import CORS
from flask import Flask, jsonify
from enum import Enum
from threading import Thread
from pymodbus.server import StartSerialServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer

# enum to represent the switch state
class TRANSFER_SWITCH(Enum):
    SOLAR = True
    MAINS = False

# set global variables
switch_value = TRANSFER_SWITCH.MAINS

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
# Function: transfer_switch
# Purpose: Simulated a Hardware-in-the-Loop transfer switch.
#   Reads coil value at 10 (00011) and switches to solar power
#   if true (value 1) or to mains power if false (value 0)
###########################################################
def transfer_switch(data_bank : ModbusSequentialDataBlock):
    global switch_value

    while True:
        # read the switch coil
        switch_coil = data_bank.getValues(10, 1)

        # set the constant
        if switch_coil:
            if switch_coil[0]:
                switch_value = TRANSFER_SWITCH.SOLAR
            else:
                switch_value = TRANSFER_SWITCH.MAINS
        _logger.debug(f"TRANSFER SWITCH: {switch_value}")

        time.sleep(constants.TS_POLL_SPEED)

###########################################################
# Function: ts_server
# Purpose: Starts the Modbus RTU server in a separate thread
###########################################################
def ts_server(context, client_com):
    StartSerialServer(context=context, port=client_com, baudrate=9600, timeout=1, framer=ModbusRtuFramer)

###########################################################
# Wrapped Function: index
# Purpose: Endpoint to return data on the transfer switch.
#   Includes only the switch state.
###########################################################
@app.route('/')
def index():
    global switch_value
    return jsonify(
        {
            "ts_state" : switch_value.value
        })

###########################################################
# Special Function: __main__
# Purpose: Sets up the Modbus RTU server for the simulated
#   HIL of the transfer switch. Takes 1 arg:
#   argv[1] = transfer switch comm port
###########################################################
if __name__ == '__main__':
    # pass args
    parser = argparse.ArgumentParser(description="Transfer Switch")
    
    # Add arguments
    parser.add_argument('-c', '--comm', type=str, help='Comm port for the transfer switch')
    parser.add_argument('-P', '--webport', type=str, help='The port number for the web server')

    # Parse the arguments
    args = parser.parse_args()
    client_com = args.comm
    webport = args.webport
    
    # (ASCII font "Big" https://patorjk.com/software/taag/#p=display&f=Big)
    title = """
        ----------------------------------------------------------------------
          _______                   __          _____         _ _       _     
         |__   __|                 / _|        / ____|       (_) |     | |    
            | |_ __ __ _ _ __  ___| |_ ___ _ _| (_____      ___| |_ ___| |__  
            | | '__/ _` | '_ \/ __|  _/ _ \ '__\___ \ \ /\ / / | __/ __| '_ \ 
            | | | | (_| | | | \__ \ ||  __/ |  ____) \ V  V /| | || (__| | | |
            |_|_|  \__,_|_| |_|___/_| \___|_| |_____/ \_/\_/ |_|\__\___|_| |_|
        ----------------------------------------------------------------------
        """
    print(title)

    # create coil default data block
    data_block = ModbusSequentialDataBlock.create()

    # create a Modbus slave context with the data block
    store = ModbusSlaveContext(co=data_block, zero_mode=True)
    context = ModbusServerContext(slaves=store, single=True)

    # start the transfer switch thread
    tp_server = Thread(target=transfer_switch, args=(data_block,))
    tp_server.daemon = True
    tp_server.start()

    # start the Modbus RTU server
    _logger.info("Starting Transfer Switch")
    tp_server = Thread(target=ts_server, args=(context, client_com))
    tp_server.daemon = True
    tp_server.start()
    
    # start flask web server (without terminal logs)
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR) 
    app.run(host="0.0.0.0", port=webport)