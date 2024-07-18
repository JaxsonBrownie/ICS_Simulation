from pyModbusTCP.server import ModbusServer, DataBank
from pymodbus.client import ModbusSerialClient
import threading
import time

# Modbus RTU client settings
RTU_PORT = '/dev/pts/9'  # Replace with your serial port
RTU_BAUDRATE = 9600
RTU_CLIENT = ModbusSerialClient(method='rtu', port=RTU_PORT, baudrate=RTU_BAUDRATE, timeout=1)
RTU_CLIENT.connect()

# Modbus TCP server settings
TCP_IP = 'localhost'
TCP_PORT = 5020
TCP_SERVER = ModbusServer(host=TCP_IP, port=TCP_PORT, no_block=True)

# Function to handle requests from TCP clients and forward them to the RTU server
def tcp_to_rtu_gateway():
    while True:
        if RTU_CLIENT.is_socket_open():
            # Read holding registers from TCP client and write to RTU server
            hr_values = DataBank.get_holding_registers(0, 10)
            RTU_CLIENT.write_registers(0, hr_values)

            # Read holding registers from RTU server and write to TCP server
            rr = RTU_CLIENT.read_holding_registers(0, 10)
            if rr.isError():
                print("Error reading from RTU server")
            else:
                DataBank.set_holding_registers(0, rr.registers)

        time.sleep(1)

# Start the Modbus TCP server
tcp_server_thread = threading.Thread(target=TCP_SERVER.start)
tcp_server_thread.daemon = True
tcp_server_thread.start()

# Start the gateway function
gateway_thread = threading.Thread(target=tcp_to_rtu_gateway)
gateway_thread.daemon = True
gateway_thread.start()

# Keep the script running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Shutdown")
    TCP_SERVER.stop()
    RTU_CLIENT.close()

#TODO: This script doesn't really work. What you need to do is copy the code from "TestSensorClient" into the
# PLC server code, and make it so very regularly (maybe every frame?) a RTU client reads from the sensors
# and writes to the data bank of the TCP server
# (only need one thread per client still!!)