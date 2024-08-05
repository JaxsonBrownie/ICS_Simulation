#!/usr/bin/env python3

import sys
import time
import logging
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

################################################################################

"""Generates a set of power (mW) values to represent a solar panels efficency over 24 hours"""
def _generate_norm_power(mean=12, std_dev=2, power_const=10.5, efficency=0.7, hours=24):
    # Note: power_const of 10.5 generates generic normal for a typical 2W rated solar panel

    # Generate 96 time intervals over 24 hours (every 15 minutes)
    x = np.linspace(0, hours, 96)

    # Generate a normal distribution representing solar generation in milliWatts (provide estimated constants)
    y = norm.pdf(x, mean, std_dev)*power_const*efficency*1000

    return y

################################################################################

"""Reads in the set of solar panel reading sets from the provided dataset"""
def _read_solar_panel_dataset(filename):
    # create dataset object for the Ausgrid dataset
    dataset = AusgridDataset()

    # read in the dataset csv file
    dataset.readFile(filename)

    # extract the required values from the dataset
    values = dataset.extract()
    pm_values = values[3]

    return pm_values


################################################################################

"""Thread to simulate power meter sensor data writing"""
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

            #_logger.info(f"SOLAR PANAL THREAD: Inc: {incr}, Value: {int(pm_data[incr])}")
            time.sleep(0.2)

################################################################################

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
    #pm_data = _generate_norm_power()
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
