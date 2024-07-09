#!/usr/bin/env python3

import time
import logging
import sys
from threading import Thread, Lock
from pyModbusTCP.client import ModbusClient
from solarSimulation import generate_norm_power

# set global variables
solar_lock = Lock()
switch_lock = Lock()
switch_solar = False # global variable to represent transfer switch state (1) = solar, (0) = mains

# create logger
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
_logger.addHandler(console_handler)

################################################################################

"""Thread to simulate a solar panel power meter PLC (sensor)"""
def solar_panel_pm(client):
    global solar_lock

    # generate set of data to represent solar power (contains 96 data points over 24 hours)
    solar_power = generate_norm_power()

    # polling loop
    incr = -1
    while True:
        # control the increment
        incr += 1
        if incr >= len(solar_power): incr = 0

        # write to holding register address 20 value of solar panel meter (40021)
        #_logger.info(f"SOLAR PANAL THREAD: Inc: {incr}, Value: {int(solar_power[incr] * 1000)}")
        with solar_lock:
            client.write_single_register(20, int(solar_power[incr] * 1000))
        time.sleep(0.2)

################################################################################

"""Thread to simulate a transfer switch PLC (actuator)"""
def transfer_switch(client : ModbusClient):
    global switch_lock, switch_solar

    # polling loop
    while True:
        # read holding register to determine whether to switch to mains (0) or solar (1)
        with switch_lock:
            switch_coil = client.read_coils(10,1)

        if switch_coil:
            if switch_coil != switch_solar:
                _logger.info(f"Transfer switch has changed: {switch_coil}")
            switch_solar = switch_coil
        else:
            _logger.error("Could not read switch coil")
        time.sleep(0.5)

################################################################################

if __name__ == '__main__':
    # init and start modbus solar panal power meter PLC client
    solar_panel_pm_client = ModbusClient(host="127.0.0.1", port=5020, unit_id=1)
    solar_tp = Thread(target=solar_panel_pm, args=(solar_panel_pm_client,))
    solar_tp.daemon = True
    _logger.info("Starting Solar Panel Power Meter Thread")
    solar_tp.start()

    
    # init and start modbus transfer switch PLC client
    transfer_switch_client = ModbusClient(host="127.0.0.1", port=5020, unit_id=2)
    tw_tp = Thread(target=transfer_switch, args=(transfer_switch_client,))
    tw_tp.daemon = True
    _logger.info("Starting Transfer Switch Thread")
    tw_tp.start()

    while True:
        # loop until stopped
        pass