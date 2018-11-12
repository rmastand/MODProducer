"""
A script to make a table of the triggers -- who could have guessed??
"""

import sys
import os
import numpy as np

trig_file_dir = sys.argv[1]

for file in os.listdir(mod_file_dir):
	trig_dict = {}
	tot_present = 0
	tot_valid = 0
	# we'll use this later for calculate the total delivered and recorded luminosities
	good_lumis = []

	with open(mod_file_dir+"/"+file, "rb") as mod_file:
		for line in mod_file: 
	

			# keeps track of the run, lumiBlock
			# this should signal each separate event
			if (("Cond" in line.split()) or ("SCond" in line.split())) and ("#" not in line.split()):
				run,lumiBlock = line.split()[1],line.split()[6]
				tot_present += 1

				if (is_lumi_valid((run,lumiBlock),lumiId_to_lumin_dict)) and (data_type == "Data"):
					tot_valid += 1		
