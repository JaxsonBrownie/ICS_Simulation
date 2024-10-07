#!/usr/bin/env python3

# Below are constant used throughout the simulation
PM_POLL_SPEED = 0.5 # polling speed used by the PLC to poll the power meter
TS_POLL_SPEED = 0.8 # speed at which the PLC polls to control the transfer switch
HMI_POLL_SPEED = 0.4 # polling speed of the HMI
PM_LOOP_SPEED = 1 # speed at which the simulated power meter cycles through its values
TS_LOOP_SPEED = 0.5 # speed at which the simulated transfer switch checks its register to switch