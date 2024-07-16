#!/bin/bash
# Run this script to create all the docker containers and to start them through Docker Compose
# Ensure Docker and Docker Compose is install on the host system

rm -r containers
mkdir containers > /dev/null 2>&1

# Function to create a container directory
create_container() {
    echo "Creating directory structure for $1"
    lowercase=$(echo "$1" | tr '[:upper:]' '[:lower:]')

    rm -r containers/$lowercase > /dev/null
    mkdir containers/$lowercase > /dev/null
    mkdir containers/$lowercase/src > /dev/null

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
#create_container PLC2 PLC2.py

# PowerMeter
create_container PowerMeter PowerMeter.py

# TransferSwitch
create_container TransferSwitch TransferSwitch.py

# Build containers
echo "Building containers"
docker compose build

# Start Docker Compose in detached mode
echo "Starting containers"
docker compose up $1