#!/usr/bin/env python3
import asyncio
import logging
import sys

from pymodbus import __version__ as pymodbus_version
from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusSlaveContext,
)
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server import (
    StartAsyncTcpServer,
)

# Create a logger
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
_logger.addHandler(console_handler)

#######################################################################################

class ModbusTCPAttributes:
    def __init__(self, ip="127.0.0.1", port=502, context=None, identity=None) -> None:
        self.ip = ip
        self.port = port
        self.context = context
        self.identity = identity

    def get_address(self):
        return (self.ip, self.port)

#######################################################################################

def setup_server():
    # Set server attributes
    ip = "0.0.0.0"
    port = 5020

    # Create sequential datablock for discrete inputs, coils, holding registers and input registers
    datablockMethod = lambda : ModbusSequentialDataBlock.create()
    context = ModbusSlaveContext(di=datablockMethod(), co=datablockMethod(), hr=datablockMethod(), ir=datablockMethod())

    # Create context with the made datablock
    context = ModbusServerContext(slaves=context, single=True)

    # Create identity
    identity = ModbusDeviceIdentification(
        info_name={
            "VendorName": "ICS_SIM",
            "ProductCode": "PM",
            "VendorUrl": "https://github.com/pymodbus-dev/pymodbus/",
            "ProductName": "PLC1",
            "ModelName": "Pymodbus Server PLC",
            "MajorMinorRevision": 1.0,
        }
    )
    
    # Finally, create the server attirbutes object and return it
    server_attributes = ModbusTCPAttributes(ip, port, context, identity)
    return server_attributes

#######################################################################################

async def run_modbus_tcp(server_attributes: ModbusTCPAttributes):
    # Get the server attributes from the created server attributes object
    address = server_attributes.get_address()
    context = server_attributes.context
    identity = server_attributes.identity

    # Start the server
    server = await StartAsyncTcpServer(context=context, identity=identity, address=address)
    return server

#######################################################################################

async def async_helper():
    server_attributes = setup_server()
    _logger.info(f"Starting PLC TCP Modbus Server (Slave) on {server_attributes.ip}:{server_attributes.port}")
      
    await run_modbus_tcp(server_attributes)


#######################################################################################

if __name__ == "__main__":
    asyncio.run(async_helper(), debug=True)

#######################################################################################