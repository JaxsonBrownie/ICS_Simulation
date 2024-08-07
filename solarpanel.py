#!/usr/bin/env python3

import csv
import random
import numpy as np
import matplotlib.pyplot as plt

# csv solar panel data file
filename = "./datasets/solar-home-data.csv"

###########################################################
# reading csv file
file_rows = []
with open(filename, 'r') as csvfile:
	csvreader = csv.reader(csvfile)
	csv_size = csvreader.line_num

	# ignore first two rows
	next(csvreader)
	next(csvreader)


	# extracting each data row one by one
	for row in csvreader:
		file_rows.append(row)

###########################################################
# filter data
filtered_rows = []
for row in file_rows:
	include_row = True
	cleaned_row = [field.strip() for field in row]

	# exclude CL (offpeak-controlled consumption) rows
	if cleaned_row[3] == "CL":
		include_row = False

	# exclude readings from solar panels of rating less than 2kW
	if float(cleaned_row[1]) < 2:
		include_row = False

	# add the row if it passes the requirements
	if include_row:
		filtered_rows.append(row)

###########################################################
# extract values for two random houses. The extracted data is as follows:
# Customr Number, Solar Panel Rating (kWp), Average Energy Consumption per day (kW), Average Solar Production per day (kWh)
extracted_values = []

# pick a random customer
customer_id = int(random.choice(filtered_rows)[0])
print(customer_id)

# extract values for that specific customer into a sub-list
customer_vals = [i for i in filtered_rows if int(i[0]) == customer_id]

###########################################################
# calculate average energy consumption for all days for selected customer
total_days = 0
total_energy = 0

for day in customer_vals:
	# check if the row is about energy consumption
	if day[3] == "GC":
		# get total energy for that day
		day_energy = sum(float(val) for val in day[5:-1])
		total_energy += day_energy
		total_days += 1

###########################################################
# extract a list of all solar panel readings across every day for the selected customer
solar_panel_readings = []
for day in customer_vals:
	if day[3] == "GG":
		day_readings = list(float(val) for val in day[5:-1])
		solar_panel_readings.append(day_readings)

# calulate average solar panel readings across all recorded days
average_solar_panel_readings = np.mean(solar_panel_readings, axis=0)

###########################################################
# print results
print("Solar Panel Rating (kWp): ", customer_vals[0][1])
print("Total days: ", total_days)
print("Total energy consumed: ", total_energy)
print("Average enery per day consumed (kWh): ", total_energy/total_days)
#print("Average energy per hour (kWh): ", total_energy/total_days/24)

print(average_solar_panel_readings)

plt.plot(average_solar_panel_readings)
plt.title('Average Solar Panel Readings over a Month')
plt.xlabel('Time (30 min intervals over one day)')
plt.ylabel('Power (kWh)')
plt.show()