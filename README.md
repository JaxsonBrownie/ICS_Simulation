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

This will created all the container directories and boot up the simulation. Note that the script uses `socat` to create serial ports for Modbus RTU communication. There may be dependency or other errors. If you have any errors please email at jokesene@outlook.com
