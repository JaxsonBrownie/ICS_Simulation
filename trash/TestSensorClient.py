from pymodbus.client import ModbusSerialClient

client = ModbusSerialClient(method='rtu', port='/dev/ttyS11', baudrate=9600, timeout=1)
client.connect()

# Read holding register at address 0
while True:
    result = client.read_holding_registers(20, 1, unit=1)
    if not result.isError():  # Check for errors
        temperature_int = result.registers[0]
        temperature = temperature_int / 10.0
        print(f'Power Meter: {result.registers} °C')
    else:
        print('Error reading holding registers')

# Close the client
#client.close()
