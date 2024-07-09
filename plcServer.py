#!/usr/bin/env python3

import logging
import sys
from pyModbusTCP.server import ModbusServer, DataBank

# create logger
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
_logger.addHandler(console_handler)

################################################################################

"""A custom ModbusServerDataBank to log changes on coils and holding registers"""
class CustomDataBank(DataBank):
    def on_holding_registers_change(self, address, from_value, to_value, srv_info):
        # control the transfer switch
        if address == 20:
            # check whether need to switch to mains (0) or keep solar (1)
            if to_value < 800:
                # switch to mains
                self.set_coils(10, [False])
            else:
                # switch to solar power
                self.set_coils(10, [True])

################################################################################

if __name__ == '__main__':
    ip = "127.0.0.1"
    port = 5020

    # init modbus server
    server = ModbusServer(host=ip, port=port, data_bank=CustomDataBank())

    title = """
        -------------------------
        ______ _     _____   __  
        | ___ \ |   /  __ \ /  | 
        | |_/ / |   | /  \/ `| | 
        |  __/| |   | |      | | 
        | |   | |___| \__/\ _| |_
        \_|   \_____/\____/ \___/
        -------------------------
        """
    print(title)
    _logger.info(f"Starting server on {ip}:{port}")
    server.start()

################################################################################