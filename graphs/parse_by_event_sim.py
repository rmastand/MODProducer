"""
make a giant table. columns: event, lumiblock, trigger present (0 or 1), triggers fired, trigger prescale
"""

import numpy as np
import sys
import ast
import os
import csv


def setw(word,n):
	return str(word)+" "*(n-len(word))
all_MOD_dirs = ["/Volumes/Drive/MITOpenLow/eos/opendata/cms/MonteCarlo2011/Summer11LegDR/QCD_Pt-0to5_TuneZ2_7Tev_pythia6/MOD/PU_S13_START53_LV6-v1/00000/"
	      ]


output_file = sys.argv[1]

lumi_id_to_lumin = 0

def is_lumi_valid(lumi_id, lumi_id_to_lumin):
	"""
	lumi_id = (run,lumiBlock)
	"""
	return True

def read_mod_file(mod_file,file_name,i,num_files,output):

	with open(mod_file) as file:
		
		for line in file:
			# MOST CODE TAKEN FROM GET_TRIGGER_INFO.py
			# keeps track of the run, lumiBlock
			# this should signal each separate event
			if "BeginEvent" in line.split():
				triggers_present = []
				triggers_prescales = []
				triggers_fired = []
				to_write = ""
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
				if is_lumi_valid((run,lumiBlock),lumi_id_to_lumin):
					to_write += setw(event,20)+setw(run,15)+setw(lumiBlock,15)
					for item in triggers_present:
						to_write += item+','
					to_write += "  "
					for item in triggers_prescales:
						to_write += item+','
					to_write += "  "
					for item in triggers_fired:
						to_write += item+','
					to_write += "\n"
					output.write(to_write)
	



with open(output_file,"w") as output:
	output.write(setw("EventNum",20)+setw("RunNum",15)+setw("LumiNum",15)+setw("Triggers Present",20)+setw("Trigger Prescales",20)+setw("Triggers Fired",20)+"\n")
	for dire in all_MOD_dirs:
		i = 1
		num_files = len(os.listdir(dire))
		
		for file in os.listdir(dire):
			# if file has not already been processed
			print "Processing file " + file + ", File "+str(i)+" of " + str(num_files)
			file_trig_dict = read_mod_file(dire+"/"+file,file,i,num_files,output)
			i += 1
	
