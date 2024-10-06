from pyModbusTCP.server import ModbusServer, DataBank

# Define a custom function code handler
def custom_function_handler(request):
    # Extract the function code from the request
    function_code = request[1]
    
    print("AJAAJAJAJ")

    # Check if function code 08 (Diagnostics) is used
    if function_code == 0x08:
        # Extract the sub-function from the request
        sub_function = (request[2] << 8) | request[3]
        
        # Handle sub-function 04 (Force Listen Only Mode)
        if sub_function == 0x0004:
            # Here you can add logic to put the server into listen-only mode
            # For demonstration purposes, let's just print a message
            print("Received request to Force Listen Only Mode")

            # Respond with an acknowledgment (same request packet back)
            return request  # Echo the request to acknowledge it
        
        # If other sub-functions are used, handle them as needed
        else:
            print(f"Unhandled sub-function: {sub_function}")
    
    # Return None for unhandled function codes (will cause an error response)
    return None

# Create a custom Modbus server
server = ModbusServer(host="0.0.0.0", port=502, no_block=True)

# Hook custom function handler into the server
server.data_hdl.custom_function = custom_function_handler

try:
    print("Starting Modbus server...")
    server.start()
except KeyboardInterrupt:
    print("Shutting down the server...")
finally:
    server.stop()

while True:
    pass