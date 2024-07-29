#!/usr/bin/env python3

import sys
import time
import logging
import numpy as np
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

"""Thread to simulate power meter sensor data writing"""
def power_meter(data_bank : ModbusSequentialDataBlock, pm_data):
    incr = -1
    while True:
        # control the increment
        incr += 1
        if incr >= len(pm_data): incr = 0

        # write to input register address 20 value of solar panel meter (40021)
        data_bank.setValues(20, [int(pm_data[incr])])
        #_logger.info(f"SOLAR PANAL THREAD: Inc: {incr}, Value: {int(pm_data[incr])}")
        time.sleep(0.2)

################################################################################

if __name__ == '__main__':
    # verify args
    if len(sys.argv) < 2:
        print("Incorrect number of arguments")
        exit(1)

    client_com = sys.argv[1]
    
    # generate dataset to simulate power meter recordings
    pm_data = _generate_norm_power()

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
