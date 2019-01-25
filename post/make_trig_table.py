import numpy as np
import datetime
import time
import sys
import ast
import os
import csv
import matplotlib.pyplot as plt

"""
USED FOR THE PAPER
ALL INFORMATION IS FOR VALID LUMIS
columns: trigger name, present events, fired events
"""

lumibyls_file = sys.argv[1]
output_table = sys.argv[2]

all_dirs = ["/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/trig/12Oct2013-v1/10000/",
	   "/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/trig/12Oct2013-v1/20000_a/",
	   "/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/trig/12Oct2013-v1/20000_b/",
	   "/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/trig/12Oct2013-v1/20000_c/",
	   "/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/trig/12Oct2013-v1/20001/"]


# key = trigger names
master_triggers_pv_lumis = {}
master_triggers_pv_events = {}
master_triggers_pvf_events = {}
total_p_events = 0
total_pv_events = 0


def read_trig_file(trig_file,file_name,i,num_files):
	"""
	prints a dict of triggers FOR EACH MOD file
	keys are triggers names (with versions)
	subdicts are lists of good lumis the trigger was present for and the corresponding good prescale values
	
	each n correponds to a different trigger name
	line n = uncut trigger name (with version)
	line n+1 = list of good lumins ids trig_dict["good_lumis"]
	line n+2 = list of good prescales trig_dict["good_prescales"]
	line n+3 = list of lumi: # times fired paired. Comes from a dict where lumi id is the key and # times fired is the value trig_dict["fired"]
	"""


	with open(trig_file) as file:
		
		for line in file:
			# MOST CODE TAKEN FROM GET_TRIGGER_INFO.py
			# keeps track of the run, lumiBlock
			# this should signal each separate event
			if ("File" in line.split()) and ("#" not in line.split()):
				total_p_events += int(line.split([2]))
				total_pv_events += int(line.split([3]))
			if ("Trig" in line.split()) and ("#" not in line.split()):
				trigger = line.split()[1][:-3]
				pv_events = int(line.split()[3])
				pvf_events = int(line.split()[4])
				try: 
					master_triggers_pv_events[trigger] += pv_events
				except KeyError:
					master_triggers_pv_events[trigger] = pv_events
				try: 
					master_triggers_pvf_events[trigger] += pvf_events
				except KeyError:
					master_triggers_pvf_events[trigger] = pvf_events


i = 1
num_files = 1223
for dire in all_dirs:
	for file in os.listdir(dire):
		# if file has not already been processed
		#print "Processing file " + file + ", File "+str(i)+" of " + str(num_files)
		read_trig_file(dire+"/"+file,file,i,num_files)
		i += 1
		

with open(output_table,"w") as output:
	output.write("trigger_name,pv_events,pvf_events\n")
	for trigger in master_triggers_pv_events,keys():
		line = trigger+","+str(master_triggers_pv_events[trigger])+","+str(master_triggers_pvf_events[trigger])+"\n"
		output.write(line)
print total_p_events,total_pv_events



