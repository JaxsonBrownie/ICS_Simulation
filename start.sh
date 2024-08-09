#!/bin/bash
# Run this script to create all the docker containers and to start them through Docker Compose
# Ensure Docker and Docker Compose is install on the host system

if [ "$EUID" -ne 0 ]; then
    echo "This script must be run as root. Please use sudo."
    exit 1
fi

# Reset container directories
rm -r containers
mkdir containers

# Create the virtual serial ports
echo "Creating virtual serial ports"
rm -r -f /dev/ttyS10 /dev/ttyS11 /dev/ttyS12 /dev/ttyS13

socat -d pty,raw,echo=0,link=/dev/ttyS10 pty,raw,echo=0,link=/dev/ttyS11 &
serial1=$!
socat -d pty,raw,echo=0,link=/dev/ttyS12 pty,raw,echo=0,link=/dev/ttyS13 &
serial2=$!
socat -d pty,raw,echo=0,link=/dev/ttyS14 pty,raw,echo=0,link=/dev/ttyS15 &
serial3=$!
socat -d pty,raw,echo=0,link=/dev/ttyS16 pty,raw,echo=0,link=/dev/ttyS17 &
serial4=$!

sleep 2

# Revoke sudo
echo "Revoking sudo"
sudo -k

# Function to create a container directory
create_container() {
    echo "Creating directory structure for $1"
    lowercase=$(echo "$1" | tr '[:upper:]' '[:lower:]')

    mkdir containers/$lowercase
    mkdir containers/$lowercase/src

    # Copy container-specific files
    cp src/$2 containers/$lowercase/src
    cp docker-files/Dockerfile containers/$lowercase

    # Copy global files to each container
    cp src/dataset.py containers/$lowercase/src
    cp src/constants.py containers/$lowercase/src
    cp datasets/solar-home-data.csv containers/$lowercase/src
}

# Function to cleanup serial ports
cleanup() {
    echo "Cleaning up serial ports"
    #kill $serial1 $serial2 $serial3 $serial4
    rm -r -f /dev/ttyS10 /dev/ttyS11 /dev/ttyS12 /dev/ttyS13 /dev/ttyS14 /dev/ttyS15 /dev/ttyS16 /dev/ttyS17
}
trap cleanup EXIT

# HMI
create_container HMI HMI.py

# PLC1
create_container PLC1 PLC.py

# PLC2
create_container PLC2 PLC.py

# PowerMeter1
create_container PowerMeter1 PowerMeter.py

# PowerMeter2
create_container PowerMeter2 PowerMeter.py

# TransferSwitch1
create_container TransferSwitch1 TransferSwitch.py

# TransferSwitch2
create_container TransferSwitch2 TransferSwitch.py

# Build containers
echo "Building containers"
docker compose build

# Start Docker Compose in detached mode
echo "Starting containers"
docker compose up $1
wait $serial1 $serial2 $serial3 $serial4