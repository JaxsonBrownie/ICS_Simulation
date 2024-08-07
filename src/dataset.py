#!/usr/bin/env python3

import csv
import random
import time
import numpy as np

###########################################################
# Class: AusgridDataset
# Purpose: passes the Ausgrid dataset to be used within the simulation
###########################################################
class AusgridDataset:
	def __init__(self):
		self.content = []
		pass

	###########################################################
	# Method: readFile
	# Purpose: reads in the dataset file into the "content" field
	###########################################################
	def readFile(self, filename):
		file_rows = []
		with open(filename, 'r') as csvfile:
			csvreader = csv.reader(csvfile)

			# ignore first two rows
			next(csvreader)
			next(csvreader)

			# extracting each data row one by one
			for row in csvreader:
				file_rows.append(row)

		# filter data
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
				self.content.append(row)

	###########################################################
	# Method: extract
	# Purpose: extracts and returns values required for the simulation.
	# 	Extract values for two random houses. The extracted data is as follows:
	# 		[
	# 		customr number, 
	# 		solar panel rating (kWp), 
	# 		average energy consumption per day (Wh), 
	# 			[
	# 			day 1 solar panel generation,
	#			day 2 solar panel generation
	#			...
	# 			],
	#		]
	###########################################################
	def extract(self):
		#extracted_values = []

		# pick a random customer
		customer_id = int(random.choice(self.content)[0])

		# extract values for that specific customer into a sub-list
		customer_vals = [i for i in self.content if int(i[0]) == customer_id]

		###########################################################
		# calculate average energy consumption for all days for selected customer
		total_days = 0
		total_energy = 0
		solar_panel_readings = []

		for day in customer_vals:
			# check if the row is about energy consumption (code for this is "GC")
			if day[3] == "GC":
				# get total energy for that day (columns 5 to end)
				day_energy = sum(float(val) for val in day[5:-1])
				total_energy += day_energy
				total_days += 1

			# extract a list of all solar panel readings across every day for the selected customer
			if day[3] == "GG":
				day_readings = list(int(float(val)*1000) for val in day[5:-1])
				solar_panel_readings.append(day_readings)

		###########################################################

		# calulate average solar panel readings across all recorded days (rounded to 3 dp and in W)
		#average_solar_panel_readings = np.mean(solar_panel_readings, axis=0)
		#average_solar_panel_readings = [int(val*1000) for val in average_solar_panel_readings]
		#average_solar_panel_readings = [round(float(val), 3) for val in average_solar_panel_readings]
		
		#extracted_values = [customer_id, customer_vals[0][1], (total_energy/total_days)*1000, [average_solar_panel_readings]]
		extracted_values = [customer_id, customer_vals[0][1], (total_energy/total_days)*1000, solar_panel_readings]

		return extracted_values

if __name__ == '__main__':
	# create dataset object for the Ausgrid dataset
	dataset = AusgridDataset()

	# read in the dataset csv file
	dataset.readFile("./datasets/solar-home-data.csv")

	# extract the required values from the dataset
	values = dataset.extract()

	pm_data = values[3]
	i = -1
	# loop through each solar panel reading for the month
	while True:
		# control the increment
		if i >= len(pm_data): i = 0
		i += 1

		for j in range(len(pm_data[i])):
			# write to input register address 20 value of solar panel meter (40021)
			#data_bank.setValues(20, [pm_data[i][j]])
			print(pm_data[i][j])

			#_logger.info(f"SOLAR PANAL THREAD: Inc: {incr}, Value: {int(pm_data[incr])}")
			time.sleep(0.3125) # this time will cycle through each day every 30 seconds (there are 48 points of data every day)