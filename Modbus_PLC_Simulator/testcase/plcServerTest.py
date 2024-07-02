#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        plcServerTest.py
#
# Purpose:     This moudle is a test case program of the lib<modbusTcpCom.py>
#              to start a Modbus-TCP server to simulate a PLC to handle holding
#              register and coils set and read request.
#
# Author:      Yuancheng Liu
#
# Created:     2023/06/11
# Version:     v_0.1.2
# Copyright:   Copyright (c) 2023 LiuYuancheng
# License:     MIT License    
#-----------------------------------------------------------------------------

import os, sys

print("Current working directory is : %s" % os.getcwd())
DIR_PATH = dirpath = os.path.dirname(os.path.abspath(__file__))
print("Current source code location : [%s]" % dirpath)

TOPDIR = 'Modbus_PLC_Simulator'
LIBDIR = 'src'

idx = dirpath.find(TOPDIR)
gTopDir = dirpath[:idx + len(TOPDIR)] if idx != -1 else dirpath   # found it - truncate right after TOPDIR
# Config the lib folder 
gLibDir = os.path.join(gTopDir, LIBDIR)
if os.path.exists(gLibDir): sys.path.insert(0, gLibDir)

#-----------------------------------------------------------------------------
print("Test import lib: ")
try:
    import modbusTcpCom
except ImportError as err:
    print("Import error: %s" % str(err))
    exit()
print("- pass")

#-----------------------------------------------------------------------------
class testLadderLogic(modbusTcpCom.ladderLogic):
    """ A test ladder logic program with 4 holding register and reverse all the 
        holding register state.
    """

    def __init__(self, parent) -> None:
        super().__init__(parent)

    def initLadderInfo(self):
        self.holdingRegsInfo['address'] = 0
        self.holdingRegsInfo['offset'] = 4
        self.srcCoilsInfo['address'] = 0
        self.srcCoilsInfo['offset'] = 4
        self.destCoilsInfo['address'] = 0
        self.destCoilsInfo['offset'] = 4

    def runLadderLogic(self, regsList, coilList=None):
        # coils will be set as the reverse state of the input registers' state. 
        result = []
        for state in regsList:
            result.append(not state)
        return result

ALLOW_R_L = ['127.0.0.1', '192.168.0.10']
ALLOW_W_L = ['127.0.0.1']

hostIp = 'localhost'
hostPort = 502

# Create a test ladder logic (?)
#testladderlogic = testLadderLogic(None)

# Create the data handler with the allow read and allow write lists
dataMgr = modbusTcpCom.plcDataHandler(allowRipList=ALLOW_R_L, allowWipList=ALLOW_W_L)

# Set up the server with host 127.0.0.1, port 502, and the created data manager
#server = modbusTcpCom.modbusTcpServer(hostIp=hostIp, hostPort=hostPort, dataHandler=dataMgr)
#server = modbusTcpCom.modbusTcpServer(hostIp=hostIp, hostPort=hostPort)
server = modbusTcpCom.modbusTcpServer(hostIp=hostIp, hostPort=hostPort, dataHandler=dataMgr)

# Get information on the server and initialise it with the data manager
serverInfo = server.getServerInfo()
dataMgr.initServerInfo(serverInfo)

# Add the test ladder logic
#dataMgr.addLadderLogic('testLogic', testladderlogic)

# Enable auto update so output coils update on holding register changes
#dataMgr.setAutoUpdate(True)

# preset some case here: 
#dataMgr.updateOutPutCoils(0, [0, 0, 0, 0])
dataMgr.updateHoldingRegs(0, [1, 2, 3, 50])

# Start the Modbus server (Slave)
print('Start server ...')
server.startServer()