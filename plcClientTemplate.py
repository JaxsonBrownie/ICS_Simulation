#!/usr/bin/env python3

""" Read 10 coils and print result on stdout. """

import time
import logging
import sys
from pyModbusTCP.client import ModbusClient

# create logger
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
_logger.addHandler(console_handler)

################################################################################

"""Sets up the client with attributes"""
def setup_client():
    client_attributes = {}
    
    client_attributes["target_ip"] = "127.0.0.1"
    client_attributes["port"] = 5020
    client_attributes["unit_id"] = 1

    return client_attributes

################################################################################

"""A simple"""
def hardware_in_loop():
    pass

################################################################################

if __name__ == '__main__':
    # setup the client
    attributes = setup_client()

    # init modbus client
    client = ModbusClient(attributes["target_ip"], attributes["port"], attributes["unit_id"])

    # main read loop
    while True:
        # read 10 bits (= coils) at address 0, store result in coils list
        coils_l = client.read_coils(0, 10)

        client.write_single_coil(5, False) if coils_l[5] else client.write_single_coil(5, True)

        # if success display registers
        if coils_l:
           _logger.info('coil ad #0 to 9: %s' % coils_l)
        else:
            _logger.info('unable to read coils')

        # sleep 2s before next polling
        time.sleep(2)
