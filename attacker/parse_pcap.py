from scapy.all import rdpcap, IP, ARP, Ether, TCP, UDP
from scapy.contrib.modbus import ModbusADURequest, ModbusADUResponse
from datetime import datetime, timezone
import csv


# path to the pcap file
PCAP_FILE = "./pcap/20241127-11:08-dataset4.pcapng"
TIMESTAMP_FILE = "./timestamps/27-29:19-timestamps.txt"
DATASET_FILE = "./datasets/Dataset2.csv"


# Function: flag_packet
# Purpose: Checks if a packet is malicious.
#   Malicious packets are either IP or ARP packets with source or
#   destination of 192.168.0.1
def flag_packet(packet):
    # initialise fields to search with
    hacker_ip = "192.168.0.1"
    is_attack = False
    
    # for IP layer packets
    if IP in packet:
        ip_layer = packet[IP]

        # check if packets is to or from the hacker (192.168.0.1)
        if ip_layer.src == hacker_ip or ip_layer.dst == hacker_ip:
            is_attack = True
    
    # for ARP packets
    if ARP in packet:
        arp_layer = packet[ARP]

        # check if it's an ARP request and the target IP matches
        if arp_layer.psrc == hacker_ip:  # 1 is ARP request
            is_attack = True
    
    return is_attack


# Function: get_protocol
# Purpose: From a Scapy packet, returns the relevant protocol as a string
def get_protocol(packet):
    protcol = ""
    if ARP in packet:
        protcol = "ARP"
    elif TCP in packet:
        # check for ModbusTCP
        if ModbusADURequest in packet or ModbusADUResponse in packet:
            protcol = "ModbusTCP"
        else:
            protcol = "TCP"
    elif UDP in packet:
        protcol = "UDP"
    elif IP in packet:
        protcol = "IP"
    #elif Ether in packet:
    #    protcol = "Ethernet"
    else:
        protcol = "Other"
    
    return protcol


# Function: reconstruct_modbus_data
# Purpose: Takes the lowest modbus Scapy layer and rebuilds the data field (only)
#   as a hex string
def reconstruct_modbus_data(modbus_layer):
    #modbus_layer = packet.getlayer(ModbusADURequest) or packet.getlayer(ModbusADUResponse)
    data_fields = {}

    # extract and reconstruct data field
    reconstructed_data = b""  # binary representation of the data field
    for field_desc in modbus_layer.fields_desc:
        field_name = field_desc.name

        if field_name in modbus_layer.fields:
            # get the value and binary representation of the field (excluding funcCode)
            if field_name != "funcCode":
                value = modbus_layer.fields[field_name]

                binary_data = field_desc.i2m(modbus_layer, value)  # Convert to binary
                data_fields[field_name] = value

                # reconstruct the data into bytes
                if isinstance(binary_data, list):
                    # convert each item in the list to bytes and concatenate
                    for item in binary_data:
                        if item == 0: # handle o item explicity for bit_length
                            reconstructed_data += b'\x00'
                        else:
                            reconstructed_data += item.to_bytes((item.bit_length() + 7) // 8, byteorder='big')
                elif isinstance(binary_data, int):
                    # convert int to bytes (big-endian format)
                    reconstructed_data += binary_data.to_bytes((binary_data.bit_length() + 7) // 8, byteorder='big')
                elif isinstance(binary_data, bytes):
                    # append raw bytes directly
                    reconstructed_data += binary_data
                else:
                    raise TypeError(f"Unexpected data type: {type(binary_data)}")

    return reconstructed_data.hex(), data_fields

# Function: get_attack_data
# Purpose: Uses the timestamp file to label each attack packet
def get_attack_data(packet):
    # define attack categories
    attack_cat = {"0":"0", "1":"0", "2":"0", "3":"1", "4":"1", "5":"N/A", "6":"N/A",
               "7":"2", "8":"2", "9":"2", "10":"2", "11":"3", "12":"3"}

    # get and format packet time
    pkt_time = datetime.fromtimestamp(float(packet.time), tz=timezone.utc)
    #pkt_time = pkt_time.strftime(f"%H:%M:%S.{int(packet.time % 1 * 1000):05d}")

    file = open(TIMESTAMP_FILE, 'r')
    lines = file.readlines()

    count = 0
    for line in lines:
        items = line.split(" : ")

        # get latest objective
        if "objective" in items[0]:
            obj = items[0]

        # convert the timestamp in the file to a datetime
        att_time = datetime.strptime(items[2].strip(), "%H:%M:%S.%f")

        # find the first items timestamp that is greater than the packets timestamp
        if att_time.time() > pkt_time.time():

            # get the attack 
            attack = items[0]
            
            # get corresponding attack category
            attack_num = ''.join(filter(str.isdigit, attack))
            if attack_num.isdigit():
                cat_num = attack_cat[attack_num]
            else:
                cat_num = "NOPE"

            # get objective number
            obj_num = ''.join(filter(str.isdigit, obj))
            return attack_num, cat_num, obj_num
        count += 1    
    return "N/A", "N/A", "N/A"


# Function: create_csv
# Purpose: Builds a CSV file from a parsed PCAP file, applying all required restrictions. 
def create_csv(packets):
    with open(DATASET_FILE, mode='w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)

        # write header row
        header = ["time", "src_mac", "dest_mac", "src_ip", "dest_ip", "protocol",
                  "length", "unit_id", "func_code", "data",
                  "attack_specific", "attack_obj", "attack_category", "attack_binary"]
        csv_writer.writerow(header)

        for pkt in packets:
            # remove UDP packets (unwanted)
            protocol = get_protocol(pkt)
            if protocol == "UDP":
                continue

            # standard packet information
            time = pkt.time
            src_mac = pkt.src if pkt.haslayer("Ethernet") else "N/A"
            dst_mac = pkt.dst if pkt.haslayer("Ethernet") else "N/A"
            src_ip = pkt["IP"].src if pkt.haslayer("IP") else "N/A"
            dst_ip = pkt["IP"].dst if pkt.haslayer("IP") else "N/A"

            # modbus specific information
            if protocol == "ModbusTCP":
                modbus_adu_layer = pkt.getlayer(3)
                modbus_layer = pkt.getlayer(4)

                length = modbus_adu_layer.len if modbus_adu_layer != None else "N/A"
                unit_id = modbus_adu_layer.unitId if modbus_adu_layer != None else "N/A"
                func_code = f'{modbus_layer.funcCode:x}' if modbus_layer != None else "N/A"

                # rebuild data field
                if modbus_layer != None:
                    data, _ = reconstruct_modbus_data(modbus_layer)
            else:
                length = "N/A"
                unit_id = "N/A"
                func_code = "N/A"
                data = "N/A"

            # attack specific information
            if flag_packet(pkt):
                attack_binary = 1

                # read the timestamps file and determine which specfic/obj/category attack it is
                attack_specific, attack_category, attack_obj = get_attack_data(pkt)
            else:
                attack_binary = 0
                attack_specific = "N/A"
                attack_category = "N/A"
                attack_obj = "N/A"

            # write to csv
            csv_writer.writerow([time, src_mac, dst_mac, src_ip, dst_ip, protocol, 
                                 length, unit_id, func_code, data, 
                                 attack_specific, attack_obj, attack_category, attack_binary])


if __name__ == "__main__":
    print(f"PCAP file: {PCAP_FILE}")
    print(f"TIMESTAMP file: {TIMESTAMP_FILE}")
    print(f"DATASET file: {DATASET_FILE}")
    print()
    print(f"Creating dataset from these files")

    # read pcap
    print(f"<1/2> Reading PCAP file: {PCAP_FILE}")
    packets = rdpcap(PCAP_FILE)

    # create dataset
    print("<2/2> Creating CSV dataset")
    create_csv(packets)

    print("Finished!")