# ICS Smart Grid Simulation
**Last Update: 9/8/2024**

## Introduction and Setup
This repository presents a simulated Smart Grid Industrial Control System. 

#### TL;DR
To begin, ensure `socat`, `docker`, `docker compose`, and `python3` is installed on your system. To run the simulation, run the script `start.sh` with root privileges, i.e: `sudo start.sh`. The simulation has been tested on 22.04.1-Ubuntu Operating System.

## Smart Grid Design
The simulation follows the design of a typical Industrial Control System (ICS). It consists of multiple components interacting together to simulate a Smart Grid. The design of the Smart Grid is as follows:

The Smart Grid consists of two houses attached to an electrical grid. Each house is connected to mains power, and each house has a solar panel installation. The Smart Grid ICS reads the energy production of each houses solar panel. If this energy production falls below a pre-determined threshold, then the Smart Grid swithes input power for that house to mains. If this energy production exceeds the threshold, then the Smart Grid switches input power back to the solar panels. The Smart Grid has a central interface that allows an operator to observe the readings and controls for the houses.

## Components
Below describes each component used to simulate the Smart Grid. Refer to further section on how these components are simulated using docker.

- **HMI (Human Machine Interface)**
    - Source file: `src/HMI.py`
    - Description: This component is the central interface that display all the data on the Smart Grid. Currently, only a terminal is used to display data.
- **PLC1 (Programmable Logic Controller)**
    - Source file: `src/PLC.py`
    - Description: This component controls the logic of the system (i.e. determining whether a house should switch to solar power or mains power). It reads values from the power meter and write to the transfer switch.
- **PLC2**
    - Source file: `src/PLC.py`
    - Description: Same as PLC1 but for the second house.
- **PowerMeter1**
    - Source file: `src/PowerMeter.py`
    - Description: Simulates a Hardware-in-the-Loop (HIL) for a power meter that records power generation from a solar panel.
- **PowerMeter2**
    - Source file: `src/PowerMeter.py`
    - Description: Same as PowerMeter1 but for the second house.
- **TransferSwitch1**
    - Source file: `src/TransferSwitch.py`
    - Description: Simulates a Hardware-in-the-Loop (HIL) for a transfer switch. A transfer switch is responsible for switching power input between two or more power sources. For this Smart Grid, this component is controlled by PLC1.
- **TransferSwitch2**
    - Source file: `src/TransferSwitch.py`
    - Description: Same as TransferSwitch1, but is controlled by PLC2 and is for the second house.

## Extra Files
Below are descriptions of other files relevant to the simulation.

- `src/constants.py`: Holds constant values that are used throughout the simulation.
- `src/dataset.py`: Contains a class that handles extracting required data from a dataset.

## Modbus Mapping
### HMI 1
- read solar panel power meter- Holding Register 20 (40021)
- read the current power input - Coil 10 (00011)

### PLC 1 & 2
Address space:
- Coil 10 (00011) - solar (ON) mains (OFF)
- Holding Register 20 (40021) - solar panel power meter (Float)

---
### Contributors:
- Jaxson Brown
    - student email: 20885504@student.curtin.edu.au
    - staff email: 295647I@curtin.edu.au

