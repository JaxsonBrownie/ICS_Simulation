## ICS Simulation
> This repo is designed to simulate an Industrial Control System

### Overview
At the root directory there are two main folders: attacker/ and simulation/
The simulation directory contains all the contents for the simulation, and the attacker directory contains the attacking scripts made by me (Jaxson).

---
### Running the Simulation
First ensure you have docker and docker-compose installed on your system:

https://docs.docker.com/engine/install/
https://docs.docker.com/compose/install/linux/#install-using-the-repository

Then move into the simulation/ directory and execute the script start.sh as sudo:
`sudo ./start.sh`
To stop the simulation, CTRL + C.

This will created all the container directories and boot up the simulation. Note that the script uses `socat` to create serial ports for Modbus RTU communication. There may be dependency or other errors. If you have any errors please email at jokesene@outlook.com

On successful startup, you'll see the containers output like this:
![image](https://github.com/user-attachments/assets/8ddbd45e-0c3c-4b31-a5b9-137d3ba12471)

---
## Viewing the Simulation
3 containers that get built are used for displaying a UI: HMI_UI, HIL1_UI, and HIL2_UI. The view the respective UI of these devices, open a browser and navigate to the following pages:
- For HMI_UI: http://localhost:1002
- For HIL1_UI: http://localhost:4001
- For HIL2_UI: http://localhost:4002

---
