#!/usr/bin/env python3

import sys
import time
import logging
import constants
import numpy as np
from dataset import AusgridDataset
from scipy.stats import norm
from threading import Thread
from pymodbus.server import StartSerialServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer

# create logger
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
_logger.addHandler(console_handler)

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
    i = -1

    # loop through each solar panel reading for the month
    while True:
        # control the increment
        if i >= len(pm_data): i = 0
        i += 1

        for j in range(len(pm_data[i])):
            # write to input register address 20 value of solar panel meter (40021)
            data_bank.setValues(20, [pm_data[i][j]])

            _logger.debug(f"SOLAR PANAL THREAD: Day: {i}, Inc: {j}, Value: {pm_data[i][j]}")
            time.sleep(constants.PM_LOOP_SPEED)

###########################################################
# Special Function: __main__
# Purpose: Sets up the Modbus RTU server for holding values
#   from the simulated HIL. Takes in one arg:
#   argv[1] = power meter comm port
###########################################################
if __name__ == '__main__':
    # verify args
    if len(sys.argv) < 2:
        print("Incorrect number of arguments")
        exit(1)

    client_com = sys.argv[1]

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
    store = ModbusSlaveContext(ir=data_block, zero_mode=True)
    context = ModbusServerContext(slaves=store, single=True)

    # start the power meter measurement update thread
    tp_server = Thread(target=power_meter, args=(data_block, pm_data))
    tp_server.daemon = True
    tp_server.start()

    # start the Modbus RTU server
    _logger.info("Starting Power Meter")
    StartSerialServer(context=context, port=client_com, baudrate=9600, timeout=1, framer=ModbusRtuFramer)
