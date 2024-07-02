#!/usr/bin/python3
#-----------------------------------------------------------------------------
# Name:        plcClientTest.py
#-----------------------------------------------------------------------------

import os
import sys
import time
from modbusPLC import modbusTcpCom

# Validate args
if len(sys.argv) != 2:
    print("Usage: <targetIp>")
    print("Exitting program")
    exit(1)

# Connect to PLC 
hostIp = sys.argv[1]
hostPort = 502

# Test Modbus connection
client = modbusTcpCom.modbusTcpClient(hostIp)
print('\nTesting modbus server connection.')
while not client.checkConn():
    print('Try connect to the PLC: %s' %hostIp)
    print(client.getCoilsBits(0, 4))
    time.sleep(0.5)
print('Connection successful')

# Function: printMenu
def printMenu(coilResult, hrResult, inc):
    os.system("clear")
    print("\n===================================================================")
    print("Increment: %s" %inc)
    print("Coils             (address:0, offset:4): %s" %coilResult)
    print("Holding Registers (address:0, offset:4): %s" %hrResult)
    print("===================================================================")

# Enter testing loop
if __name__ == "__main__":
    inc = 0

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

"""
#-----------------------------------------------------------------------------
print('\nTestcase 02: read the coils: ')
result = client.getCoilsBits(4, 5)
correctResult = [False, False, False, False, False]
if result == correctResult: 
    print(" - test Pass, result: %s" %str(result))
else:
    print(" - test Fail, result: %s" %str(result))
time.sleep(0.5)

#-----------------------------------------------------------------------------

print('\nTestCase 03: read the holding registers')
result = client.getHoldingRegs(0, 4)
correctResult = [1, 2, 3, 50]
if result == correctResult: 
    print(" - test Pass, result: %s" %str(result))
else:
    print(" - test Fail, result: %s" %str(result))
time.sleep(0.5)

#-----------------------------------------------------------------------------

print('\nTestcase 04: Set the holding registers')
client.setHoldingRegs(1, 20)
time.sleep(0.5)
result = client.getHoldingRegs(0, 4)
correctResult = [1, 20, 3, 50]
if result == correctResult: 
    print(" - test Pass, result: %s" %str(result))
else:
    print(" - test Fail, result: %s" %str(result))
time.sleep(0.5)

#-----------------------------------------------------------------------------

#print('\nTestcase 05: check auto update coils function')
#result = client.getCoilsBits(0, 4)
#if result == [True, False, False, False]: 
#    print(" - test Pass, result: %s" %str(result))
#else:
#    print(" - test Fail, result: %s" %str(result))
#time.sleep(0.5)

#-----------------------------------------------------------------------------

print('\nTestcase 06: Set the coils')
client.setCoilsBit(1, 1)
time.sleep(0.5)
result = client.getCoilsBits(0, 6)
correctResult = [False, True, False, False, False, False]
if result == correctResult: 
    print(" - test Pass, result: %s" %str(result))
else:
    print(" - test Fail, result: %s" %str(result))
time.sleep(0.5)
"""

