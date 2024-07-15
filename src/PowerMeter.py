#!/usr/bin/env python3

import time
import logging
import sys
import numpy as np
from scipy.stats import norm
from threading import Thread, Lock
from pyModbusTCP.client import ModbusClient

# set global variables
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

"""Thread to simulate power meter sensor data writing"""
def power_meter(client : ModbusClient, pm_data):
    global lock

    incr = -1
    while True:
        # control the increment
        incr += 1
        if incr >= len(pm_data): incr = 0

        # write to holding register address 20 value of solar panel meter (40021)
        _logger.info(f"SOLAR PANAL THREAD: Inc: {incr}, Value: {int(pm_data[incr])}")
        with lock:
            client.write_single_register(20, int(pm_data[incr]))
        time.sleep(0.2)

################################################################################

"""Generates a set of power (mW) values to represent a solar panels efficency over 24 hours"""
#TODO: Create this as a seperate HIL component using UDP electrical signal simulation
def _generate_norm_power(mean=12, std_dev=2, power_const=10.5, efficency=0.7, hours=24):
    # Note: power_const of 10.5 generates generic normal for a typical 2W rated solar panel

    # Generate 96 time intervals over 24 hours (every 15 minutes)
    x = np.linspace(0, hours, 96)

    # Generate a normal distribution representing solar generation in milliWatts (provide estimated constants)
    y = norm.pdf(x, mean, std_dev)*power_const*efficency*1000

    return y

################################################################################

if __name__ == '__main__':
    # verify args
    if len(sys.argv) < 2:
        print("Incorrect number of arguments")
        exit(1)
    
    target_ip = sys.argv[1]

    # init modbus client
    client = ModbusClient(host=target_ip, port=5020, unit_id=1)

    # generate dataset to simulate power meter recordings
    pm_data = _generate_norm_power()

    # start the HIL client thread
    tp = Thread(target=power_meter, args=(client, pm_data))
    tp.daemon = True # to kill the thread when the main thread exits
    tp.start()

    _logger.info("Starting HMI Client")
    
    # (ASCII font "Big" https://patorjk.com/software/taag/#p=display&f=Big)
    title = """
        ---------------------------
        <todo>
        ---------------------------
        """
    print(title)

    while True:
        time.sleep(0.5)