from pymodbus.server import StartSerialServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer
import random
import time
import threading

# Function to update the temperature value in the Modbus register
def update_temperature_data_block(data_block):
    while True:
        # Simulate a temperature reading (e.g., between 20 and 30 degrees Celsius)
        temperature = random.uniform(20, 30)
        # Convert temperature to an integer representation (e.g., 25.5 -> 255)
        temperature_int = int(temperature * 10)
        # Update the data block with the new temperature value
        data_block.setValues(0, [temperature_int])
        time.sleep(1)  # Update the temperature every second

# Create a data block with an initial temperature value
data_block = ModbusSequentialDataBlock(0, [250])  # Initial temperature 25.0°C

# Create a Modbus slave context with the data block
store = ModbusSlaveContext(hr=data_block, zero_mode=True)
context = ModbusServerContext(slaves=store, single=True)

# Create device identification (optional)
identity = ModbusDeviceIdentification()
identity.VendorName = 'MyCompany'
identity.ProductCode = 'TS'
identity.VendorUrl = 'http://mycompany.com'
identity.ProductName = 'Temperature Sensor'
identity.ModelName = 'TS-100'
identity.MajorMinorRevision = '1.0'

# Start the temperature update thread
temperature_thread = threading.Thread(target=update_temperature_data_block, args=(data_block,))
temperature_thread.daemon = True
temperature_thread.start()

# Start the Modbus RTU server
StartSerialServer(context=context, identity=identity, port='/dev/pts/5', baudrate=9600, timeout=1, framer=ModbusRtuFramer)
