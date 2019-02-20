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

# setting the ordering
all_triggers = ["HLT_Jet30","HLT_Jet60","HLT_Jet80","HLT_Jet110","HLT_Jet150","HLT_Jet190","HLT_Jet240","HLT_Jet300",
		"HLT_Jet370","HLT_Jet800","HLT_DiJetAve30",
		"HLT_DiJetAve60","HLT_DiJetAve80","HLT_DiJetAve110","HLT_DiJetAve150","HLT_DiJetAve190",
		"HLT_DiJetAve240","HLT_DiJetAve300","HLT_DiJetAve370","HLT_DiJetAve15U","HLT_DiJetAve30U","HLT_DiJetAve50U",
		"HLT_DiJetAve70U","HLT_DiJetAve100U",
		"HLT_DiJetAve140U","HLT_DiJetAve180U","HLT_DiJetAve300U",
		"HLT_Jet240_CentralJet30_BTagIP","HLT_Jet270_CentralJet30_BTagIP","HLT_Jet370_NoJetID"]
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





def read_trig_file(trig_file,file_name,total_p_events, total_pv_events):
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

				total_p_events += int(line.split()[2])
				total_pv_events += int(line.split()[3])
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
	return total_p_events, total_pv_events
total_p_events, total_pv_events = 0,0
i = 1
num_files = 1223
for dire in all_dirs:
	for file in os.listdir(dire):
		# if file has not already been processed
		#print "Processing file " + file + ", File "+str(i)+" of " + str(num_files)
		total_p_events, total_pv_events = read_trig_file(dire+"/"+file,file,total_p_events, total_pv_events)
		i += 1
		
		
		

with open(output_table,"w") as output:
	output.write("trigger_name,pv_events,pvf_events\n")
	for trigger in all_triggers:
		line = "\\texttt{"+trigger.replace("_","\_")+"}"+","+str(master_triggers_pv_events[trigger])+","+str(master_triggers_pvf_events[trigger])+"\n"
		output.write(line)
	line = "Total" + "," + "0" + "," + "0" + "\n"
	output.write(line)
print total_p_events,total_pv_events



