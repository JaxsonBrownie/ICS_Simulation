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

# enum to represent the switch state
class TRANSFER_SWITCH(Enum):
    SOLAR = True
    MAINS = False

# set global variables
switch_value = TRANSFER_SWITCH.MAINS
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

# create powermeter flask app
pm_app = Flask(__name__)
CORS(pm_app)

# create transfer switch flask app
ts_app = Flask(__name__)
CORS(ts_app)

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
# Function: pm_server
# Purpose: Starts the Modbus RTU server in a separate thread
###########################################################
def pm_server(context, client_com):
    StartSerialServer(context=context, port=client_com, baudrate=9600, timeout=1, framer=ModbusRtuFramer)

###########################################################
# Function: ts_server
# Purpose: Starts the Modbus RTU server in a separate thread
###########################################################
def ts_server(context, client_com):
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
# Purpose: Sets up the Modbus RTU server for holding values
#   from the simulated HIL.
###########################################################
if __name__ == '__main__':
    # pass args
    parser = argparse.ArgumentParser(description="Hardware-in-the-Loop")
    
    # Add arguments
    parser.add_argument('-c', '--comm', type=str, help='Comm port for the serial Modbus server')
    parser.add_argument('-s1', '--pm_slave', type=int, help='Modbus RTU slave id for the power meter')
    parser.add_argument('-s2', '--ts_slave', type=int, help='Modbus RTU slave id for the transfer switch')
    parser.add_argument('-P1', '--pm_webport', type=int, help='The port number for the power meter web server')
    parser.add_argument('-P2', '--ts_webport', type=int, help='The port number for the transfer switch web server')

    # Parse the arguments
    args = parser.parse_args()
    comm = args.comm
    pm_slave_id = args.pm_slave
    ts_slave_id = args.ts_slave
    pm_webport = args.pm_webport
    ts_webport = args.ts_webport

    # (ASCII font "Big" https://patorjk.com/software/taag/#p=display&f=Big)
    title = """
        ---------------------
         _    _ _____ _      
        | |  | |_   _| |     
        | |__| | | | | |     
        |  __  | | | | |     
        | |  | |_| |_| |____ 
        |_|  |_|_____|______|
        ---------------------
        """
    print(title)

    # generate dataset to simulate power meter recordings
    pm_data = _read_solar_panel_dataset("solar-home-data.csv")  # note: this csv file gets copied into the directory when the containers are made

    # create data blocks for the pm and ts
    pm_data_block = ModbusSequentialDataBlock.create()
    ts_data_block = ModbusSequentialDataBlock.create()

    # create pm slave
    pm_slave = ModbusSlaveContext(ir=pm_data_block, zero_mode=True)
    
    # create ts slave
    ts_slave = ModbusSlaveContext(co=ts_data_block, zero_mode=True)
    
    # create the context for the two slaves
    context = ModbusServerContext(slaves={pm_slave_id : pm_slave, ts_slave_id : ts_slave}, single=False)

    # start the power meter measurement update thread
    tp_pm = Thread(target=power_meter, args=(pm_data_block, pm_data))
    tp_pm.daemon = True
    tp_pm.start()

    # start the transfer switch thread
    tp_server = Thread(target=transfer_switch, args=(ts_data_block,))
    tp_server.daemon = True
    tp_server.start()

    # start the Modbus RTU server
    _logger.info("Starting Power Meter")
    tp_server = Thread(target=pm_server, args=(context, comm))
    tp_server.daemon = True
    tp_server.start()

    # start flask web servers (without terminal logs)
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR) 
    pm_app.run(host="0.0.0.0", port=pm_webport)
    ts_app.run(host="0.0.0.0", port=ts_webport)
