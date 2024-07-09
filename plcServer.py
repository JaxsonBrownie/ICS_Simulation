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
    def on_coils_change(self, address, from_value, to_value, srv_info):
        """Call by server when change occur on coils space."""
        msg = 'change in coil space [{0!r:^5} > {1!r:^5}] at @ 0x{2:04X} from ip: {3:<15}'
        msg = msg.format(from_value, to_value, address, srv_info.client.address)
        _logger.info(msg)

    def on_holding_registers_change(self, address, from_value, to_value, srv_info):
        """Call by server when change occur on holding registers space."""
        msg = 'change in hreg space [{0!r:^5} > {1!r:^5}] at @ 0x{2:04X} from ip: {3:<15}'
        msg = msg.format(from_value, to_value, address, srv_info.client.address)
        _logger.info(msg)

################################################################################

"""Sets up the server with attributes"""
def setup_server():
    server_attributes = {}
    
    server_attributes["ip"] = "127.0.0.1"
    server_attributes["port"] = 5020
    server_attributes["data_bank"] = CustomDataBank()

    return server_attributes

################################################################################

if __name__ == '__main__':
    # setup the server
    attributes = setup_server()

    # init modbus server
    server = ModbusServer(host=attributes["ip"], port=attributes["port"], data_bank=attributes["data_bank"])

    _logger.info(f"Starting server on {attributes['ip']}:{attributes['port']}")
    server.start()

################################################################################