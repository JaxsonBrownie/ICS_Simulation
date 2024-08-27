#!/usr/bin/env python3

import sys
import time
import logging
import constants
import numpy as np
import argparse
from flask_cors import CORS
from dataset import AusgridDataset
from scipy.stats import norm
from threading import Thread
from flask import Flask, jsonify
from pymodbus.server import StartSerialServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer

# set global variables
pm_reading = 0
time_reading = 0

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
# Private Function: generate_norm_power
# Purpose: Generates a simulated set of data points that
#   represent solar panel generation over a day. Uses a
#   normal distribution (bell-curve) to represent this data
###########################################################
def _generate_norm_power(mean=12, std_dev=2, power_const=10.5, efficency=0.7, hours=24):
    # Note: power_const of 10.5 generates generic normal for a typical 2W rated solar panel

    # Generate 96 time intervals over 24 hours (every 15 minutes)
    x = np.linspace(0, hours, 96)

    # Generate a normal distribution representing solar generation in milliWatts (provide estimated constants)
    y = norm.pdf(x, mean, std_dev)*power_const*efficency*1000

    return y

###########################################################
# Private Function: read_solar_panel_dataset
# Purpose: Creates an AusgridDataset object to read in and
#   extract data points for solar panel readings. This
#   dataset is taken from real-world readings of households
#   in NSW.
###########################################################
def _read_solar_panel_dataset(filename):
    # create dataset object for the Ausgrid dataset
    dataset = AusgridDataset()

    # read in the dataset csv file
    dataset.readFile(filename)

    # extract the required values from the dataset
    values = dataset.extract()
    pm_values = values[3]

    return pm_values


###########################################################
# Function: power_meter
# Purpose: Simulates a Hardware-in-the-Loop process of a
#   power meter reading power input from a solar panel.
#   Writes recorded values to input register 20 (40021)
###########################################################
def power_meter(data_bank : ModbusSequentialDataBlock, pm_data):
    global pm_reading, time_reading
    i = -1

    # loop through each solar panel reading for the month
    while True:
        # control the increment
        if i >= len(pm_data): i = 0
        i += 1

        for j in range(len(pm_data[i])):
            # write to input register address 20 value of solar panel meter (40021)
            pm_reading = pm_data[i][j]
            data_bank.setValues(20, [pm_reading])

            _logger.debug(f"SOLAR PANAL THREAD: Day: {i}, Inc: {j}, Value: {pm_reading}")
            time_reading += 30
            time.sleep(constants.PM_LOOP_SPEED)

###########################################################
# Function: pm_server
# Purpose: Starts the Modbus RTU server in a separate thread
###########################################################
def pm_server(context, client_com):
    StartSerialServer(context=context, port=client_com, baudrate=9600, timeout=1, framer=ModbusRtuFramer)

###########################################################
# Wrapped Function: index
# Purpose: Endpoint to return data on the power meter.
#   Includes data on the power meter readings and time.
###########################################################
@app.route('/')
def index():
    global pm_reading, time_reading
    return jsonify(
        {
            "pm_reading" : pm_reading,
            "time" : time_reading
        })
###########################################################
# Special Function: __main__
# Purpose: Sets up the Modbus RTU server for holding values
#   from the simulated HIL.
###########################################################
if __name__ == '__main__':
    # pass args
    parser = argparse.ArgumentParser(description="Power Meter")
    
    # Add arguments
    parser.add_argument('-c', '--comm', type=str, help='Comm port for the power meter')
    parser.add_argument('-s', '--slave', type=int, help='Modbus RTU slave id')
    parser.add_argument('-P', '--webport', type=str, help='The port number for the web server')

    # Parse the arguments
    args = parser.parse_args()
    client_com = args.comm
    slave_id = args.slave
    webport = args.webport

    # (ASCII font "Big" https://patorjk.com/software/taag/#p=display&f=Big)
    title = """
        ------------------------------------------------------
         _____                       __  __      _
        |  __ \                     |  \/  |    | |
        | |__) |____      _____ _ __| \  / | ___| |_ ___ _ __
        |  ___/ _ \ \ /\ / / _ \ '__| |\/| |/ _ \ __/ _ \ '__|
        | |  | (_) \ V  V /  __/ |  | |  | |  __/ ||  __/ |
        |_|   \___/ \_/\_/ \___|_|  |_|  |_|\___|\__\___|_|
        ------------------------------------------------------
        """
    print(title)

    # generate dataset to simulate power meter recordings
    pm_data = _read_solar_panel_dataset("solar-home-data.csv")  # note: this csv file gets copied into the directory when the containers are made

    # create input register default data block
    data_block = ModbusSequentialDataBlock.create()

    # create a Modbus slave context with the data block
    slave = ModbusSlaveContext(ir=data_block, zero_mode=True)
    context = ModbusServerContext(slaves={slave_id: slave}, single=False)

    # start the power meter measurement update thread
    tp_pm = Thread(target=power_meter, args=(data_block, pm_data))
    tp_pm.daemon = True
    tp_pm.start()

    # start the Modbus RTU server
    _logger.info("Starting Power Meter")
    tp_server = Thread(target=pm_server, args=(context, client_com))
    tp_server.daemon = True
    tp_server.start()

    # start flask web server (without terminal logs)
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR) 
    app.run(host="0.0.0.0", port=webport)

















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
    parser.add_argument('-s', '--slave', type=int, help='Modbus RTU slave id')
    parser.add_argument('-P', '--webport', type=str, help='The port number for the web server')

    # Parse the arguments
    args = parser.parse_args()
    client_com = args.comm
    slave_id = args.slave
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
    slave = ModbusSlaveContext(co=data_block, zero_mode=True)
    context = ModbusServerContext(slaves={slave_id: slave}, single=False)

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