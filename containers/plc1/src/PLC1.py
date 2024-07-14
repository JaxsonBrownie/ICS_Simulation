#!/usr/bin/env python3

import logging
import sys
from threading import Thread, Lock
import time
from pyModbusTCP.server import ModbusServer, DataBank

# set global variables
#solar_panel_pm = []
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

"""
Inherited Class: DataBankLogic
Purpose: A custom ModbusServerDataBank to control logic within the PLC
"""
class DataBankLogic(DataBank):
    """
    Overrided Function: on_holding_registers_change
    Purpose: Defines logic to be executed when a holding register value changes
    """
    def on_holding_registers_change(self, address, from_value, to_value, srv_info):
        # control the transfer switch
        if address == 20:
            self.__transfer_switch_logic(to_value, 800, 10)

    """
    Private Function: transfer_switch_logic
    Purpose: Simulates the transfer swtich logic
    """
    def __transfer_switch_logic(self, power, power_thresh, switch_addr):
        # check whether need to switch to mains (0) or keep solar (1)
        if power < power_thresh:
            # switch to mains
            self.set_coils(switch_addr, [False])
        else:
            # switch to solar power
            self.set_coils(switch_addr, [True])


################################################################################

"""Thread for the PLC server"""
def plc_server(server : ModbusServer):
    _logger.info(f"Starting PLC1 Server")
    server.start()

################################################################################

if __name__ == '__main__':
    server_ip = "127.0.0.1"
    server_port = 5020

    client_target_ip = "127.0.0.1"
    client_target_port = 5020

    # (ASCII font "Big" https://patorjk.com/software/taag/#p=display&f=Big)
    title = """
        -------------------------
         _____  _      _____ __ 
        |  __ \| |    / ____/_ |
        | |__) | |   | |     | |
        |  ___/| |   | |     | |
        | |    | |___| |____ | |
        |_|    |______\_____||_|
        -------------------------
        """
    print(title)

    # init modbus server
    server = ModbusServer(host=server_ip, port=server_port, data_bank=DataBankLogic())

    # start the PLC server thread
    tp_server = Thread(target=plc_server, args=(server,))
    tp_server.daemon = True
    tp_server.start()

    while True:
        with lock:
            print()
        
        time.sleep(1)

################################################################################