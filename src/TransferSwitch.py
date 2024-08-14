#!/usr/bin/env python3

import time
import logging
import sys
import constants
import argparse
from enum import Enum
from threading import Thread
from pymodbus.server import StartSerialServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer

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

###########################################################
# Function: transfer_switch
# Purpose: Simulated a Hardware-in-the-Loop transfer switch.
#   Reads coil value at 10 (00011) and switches to solar power
#   if true (value 1) or to mains power if false (value 0)
###########################################################
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
        _logger.debug(f"TRANSFER SWITCH: {switch_value}")

        time.sleep(constants.TS_POLL_SPEED)

###########################################################
# Special Function: __main__
# Purpose: Sets up the Modbus RTU server for the simulated
#   HIL of the transfer switch. Takes 1 arg:
#   argv[1] = transfer switch comm port
###########################################################
if __name__ == '__main__':
    # pass args
    parser = argparse.ArgumentParser(description="Human Machine Interface")
    
    # Add arguments
    parser.add_argument('-c', '--comm', type=str, help='Comm port for the transfer switch')

    # Parse the arguments
    args = parser.parse_args()
    client_com = args.comm
    
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
    StartSerialServer(context=context, port=client_com, baudrate=9600, timeout=1, framer=ModbusRtuFramer)