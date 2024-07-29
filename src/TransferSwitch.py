#!/usr/bin/env python3

import time
import logging
import sys
from enum import Enum
from threading import Thread, Lock
from pymodbus.server import StartSerialServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer

# set global variables
#lock = Lock()

# enum to represent the switch state
class TRANSFER_SWITCH(Enum):
    SOLAR = True
    MAINS = False

# create logger
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
_logger.addHandler(console_handler)

################################################################################

"""Thread to simulate the transfer switch actuator"""
def transfer_switch(data_bank : ModbusSequentialDataBlock):
    # default switch value
    switch_value = TRANSFER_SWITCH.MAINS

    while True:
        # read the switch coil
        switch_coil = data_bank.getValues(10, 1)

        # set the constant
        if switch_coil:
            if switch_coil[0]:
                switch_value = TRANSFER_SWITCH.SOLAR
            else:
                switch_value = TRANSFER_SWITCH.MAINS
        #_logger.info(f"TRANSFER SWITCH: {switch_value}")

        time.sleep(2)

################################################################################

if __name__ == '__main__':
    # verify args
    if len(sys.argv) < 2:
        print("Incorrect number of arguments")
        exit(1)

    client_com = sys.argv[1]
    
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
    StartSerialServer(context=context, port=client_com, baudrate=9600, timeout=1, framer=ModbusRtuFramer)