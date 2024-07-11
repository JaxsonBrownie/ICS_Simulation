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

"""
Inherited Class: DataBankLogic
Purpose: A custom ModbusServerDataBank to control logic within the PLC
"""
class DataBankLogic(DataBank):
    """
    Function: transfer_switch_logic
    Purpose: Simulates the transfer swtich logic. When the supplied milliwattage
        from the holding register is below the given power
        threshold, power input will switch to mains and vice versa via given coil.
    """
    def __transfer_switch_logic(self, power, power_thresh, switch_addr):
        # check whether need to switch to mains (0) or keep solar (1)
        if power < power_thresh:
            # switch to mains
            self.set_coils(switch_addr, [False])
        else:
            # switch to solar power
            self.set_coils(switch_addr, [True])

    """
    Overrided Function: on_holding_registers_change
    Purpose: Defines logic to be executed when a holding register value changes
    """
    def on_holding_registers_change(self, address, from_value, to_value, srv_info):
        # control the transfer switch
        if address == 20:
            self.__transfer_switch_logic(to_value, 800, 10)

################################################################################

if __name__ == '__main__':
    ip = "127.0.0.1"
    port = 5020

    # init modbus server
    server = ModbusServer(host=ip, port=port, data_bank=DataBankLogic())

    # (ASCII font "Big" https://patorjk.com/software/taag/#p=display&f=Big)
    title = """
        -------------------------
         _____  _      _____ ___  
        |  __ \| |    / ____|__ \ 
        | |__) | |   | |       ) |
        |  ___/| |   | |      / / 
        | |    | |___| |____ / /_ 
        |_|    |______\_____|____|
        -------------------------
        """
    print(title)
    _logger.info(f"Starting PLC 2 on {ip}:{port}")
    server.start()

################################################################################