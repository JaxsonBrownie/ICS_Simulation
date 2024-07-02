#!/usr/bin/python3
#-----------------------------------------------------------------------------
# Name:        modbusServer.py
#-----------------------------------------------------------------------------

import os, sys
from modbusPLC import modbusTcpCom

# Allow reading and writing for all PLCs (don't include to have them all allowed by default)
#ALLOW_R_L = ['127.0.0.1', '192.168.10.21']
#ALLOW_W_L = ['127.0.0.1']

# Serve on all interfaces
hostIp = '0.0.0.0'
hostPort = 502

# Create the data handler and server
dataMgr = modbusTcpCom.plcDataHandler(None)
server = modbusTcpCom.modbusTcpServer(hostIp=hostIp, hostPort=hostPort, dataHandler=dataMgr)

# Get information on the server and initialise it with the data manager
serverInfo = server.getServerInfo()
dataMgr.initServerInfo(serverInfo)

# Preset values (default is 0 for both coils and registers)
dataMgr.updateOutPutCoils(0, [0, 1, 0, 1])
dataMgr.updateHoldingRegs(0, [1, 2, 3, 50])

# Start the Modbus server (Slave)
print('Starting Modbus TCP server ...')
server.startServer()