#!/bin/bash
# Run this script to create all the docker containers and to start them through Docker Compose
# Ensure Docker and Docker Compose is install on the host system

rm -r containers
mkdir containers

# Function to create a container directory
create_container() {
    echo "Creating directory structure for $1"
    lowercase=$(echo "$1" | tr '[:upper:]' '[:lower:]')

    rm -r containers/$lowercase
    mkdir containers/$lowercase
    mkdir containers/$lowercase/src

    cp src/$2 containers/$lowercase/src
    cp docker-files/Dockerfile containers/$lowercase
}

# HMI1
create_container HMI1 HMI1.py

# HMI2
#create_container HMI2 HMI2.py

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