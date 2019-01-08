"""
make a giant table. columns: event, lumiblock, trigger present (0 or 1), triggers fired, trigger prescale
"""

import numpy as np
import datetime
import time
import sys
import ast
import os
import csv


def setw(word,n):
	return str(word)+" "*(n-len(word))

"""generates file trig dicts, prints them to 1 dict for each file"""

lumibyls_file = sys.argv[1]
mod_file_inpur_dir = sys.argv[2]
output_file = sys.argv[3]

def read_lumi_by_ls(lumibyls_file):
	"""
	returns two dicts with keys = (run,lumiBlock)
	1st values: gps times
	2nd values: (lumi_delivered, lumi_recorded)
	"""
	lumibyls = open(lumibyls_file)
	lines =  lumibyls.readlines()
	split_lines = [line.split(",") for line in lines][2:]
	char = ""
	lumi_id_to_gps_times = {}
	lumi_id_to_lumin = {}
	i = 0
	while char !="#":
		run = split_lines[i][0].split(":")[0]
		lumi = split_lines[i][1].split(":")[0]
		date = split_lines[i][2].split(" ")[0]
		tim = split_lines[i][2].split(" ")[1]
		mdy = [int(x) for x in date.split("/")]
		hms = [int(x) for x in tim.split(":")]
		dt = datetime.datetime(mdy[2], mdy[0], mdy[1], hms[0], hms[1],hms[2])
		lumi_id_to_gps_times[(run,lumi)] = time.mktime(dt.timetuple())
		lumi_id_to_lumin[(run,lumi)] = (float(split_lines[i][5]),float(split_lines[i][6]))
		i += 1
		try:
			char = split_lines[i][0][0]
		except: pass
	return lumi_id_to_gps_times,lumi_id_to_lumin

def is_lumi_valid(lumi_id, lumi_id_to_lumin):
	"""
	lumi_id = (run,lumiBlock)
	"""
	try:
		luminosity = lumi_id_to_lumin[lumi_id]
		return 1
	except KeyError:
		pass

lumi_id_to_gps_times,lumi_id_to_lumin = read_lumi_by_ls(lumibyls_file)


def read_mod_file(mod_file,file_trig_dict_output_dir,file_name,i,num_files,output):

	with open(mod_file) as file:
		
		for line in file:
			# MOST CODE TAKEN FROM GET_TRIGGER_INFO.py
			# keeps track of the run, lumiBlock
			# this should signal each separate event
			if "BeginEvent" in line.split():
				triggers_present = []
				triggers_prescales = []
				triggers_fired = []
				line = ""
			elif ("Cond" in line.split()) and ("#" not in line.split()):
				# means we hit a new event
				run,event,lumiBlock = line.split()[1],line.split()[2],line.split()[3]

			elif ("Trig" in line.split()) and ("#" not in line.split()):
				# all within 1 event
				# given line: [Trig identifier, trig name, prescale1, prescale2, fired?]
				
				if is_lumi_valid((run,lumiBlock),lumi_id_to_lumin):
					triggers_present.append(line.split()[1])
					triggers_prescales.append(str(float(line.split()[2])*float(line.split()[3])))
					if int(line.split()[4]) == 1:
						triggers_fired.append(line.split()[1])
						
			
			elif "EndEvent" in line.split():
				line += setw(event,10)+setw(run,10)+setw(lumiBlock,10)
				for item in triggers_present:
					line += item+',"
				line += "  "
				for item in triggers_prescales:
					line += item+',"
				line += "  "
				for item in triggers_fired:
					line += item+',"
				line += "\n"
				output_file.write(line)
	

i = 1
num_files = len(os.listdir(mod_file_inpur_dir))
with open(output_file,"w") as output:
	output.write(setw("EventNum",10)+setw("RunNum",10)+setw("LumiNum",10)+setw("Triggers Present",20)+setw("Trigger Prescales",20)+setw("Triggers Fired",20)+"\n")

	for file in os.listdir(mod_file_inpur_dir):
		# if file has not already been processed
		print "Processing file " + file + ", File "+str(i)+" of " + str(num_files)
		file_trig_dict = read_mod_file(mod_file_inpur_dir+"/"+file,file_trig_dict_output_dir,file,i,num_files,output)
		i += 1
	
