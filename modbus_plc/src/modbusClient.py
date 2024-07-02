#!/usr/bin/python3
#-----------------------------------------------------------------------------
# Name:        plcClientTest.py
#-----------------------------------------------------------------------------

import os
import sys
import time
from modbusPLC import modbusTcpCom

# Function: main
def main(args):
    # Validate args
    if len(args) != 2:
        print("Usage: <targetIp>")
        print("Exitting program")
        exit(1)

    # Connect to PLC 
    hostIp = args[1]
    hostPort = 502

    # Test Modbus connection
    client = modbusTcpCom.modbusTcpClient(hostIp)
    testConnection(client, hostIp)
    inc = 0

    # Loop the polling
    while True:
        inc += 1
        addr = 0
        length = 4
        print("\nPolling coils with address %s and length %s:" %(addr, length))
        coilResult = client.getCoilsBits(0, 4)
        print("\nPolling holding registers with address %s and length %s:" %(addr, length))
        hrResult = client.getHoldingRegs(0, 4)

        printMenu(coilResult, hrResult, inc)
        time.sleep(1)


# Function: testConnection
def testConnection(client, hostIp):
    print('\nTesting modbus server connection.')
    while not client.checkConn():
        print('Try connect to the PLC: %s' %hostIp)
        print(client.getCoilsBits(0, 4))
        time.sleep(0.5)
    print('Connection successful')
    return True

# Function: printMenu
def printMenu(coilResult, hrResult, inc):
    os.system("clear")
    print("\n=========================================================================")
    print("Polling Increment: %s" %inc)
    print("Coils             (address:0, offset:4): %s" %coilResult)
    print("Holding Registers (address:0, offset:4): %s" %hrResult)
    print("=========================================================================")

# Main
if __name__ == "__main__":
    main(sys.argv)
    