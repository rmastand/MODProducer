import numpy as np
import sys
import os
import datetime
import time
import csv
import matplotlib.pyplot as plt

parsed_file_inpur_dir = sys.argv[1]
lumibyls_file = sys.argv[2]
run_alumi_file = sys.argv[3]

runA_runs = []
read_alumi_lines = open(run_alumi_file,"r").readlines()
for line in read_alumi_lines[4:]:
  char = line[0]
  if char != "+":
    runA_runs.append(line.split()[1].split(":")[0])
  else:
    break
print "Done reading in ALumi"


def cut_trigger_name(name):
	"""removes the version number from the trigger names"""
	return name.rsplit("_", 1)[0]

# good_lumis,good_prescales
master_trig_dict = {"HLT_Jet190":{"good_lumis":[],"good_prescales":[],"fired":{}},"HLT_Jet370":{"good_lumis":[],"good_prescales":[],"fired":{}},
					"HLT_Jet150":{"good_lumis":[],"good_prescales":[],"fired":{}},"HLT_Jet240":{"good_lumis":[],"good_prescales":[],"fired":{}},
					"HLT_Jet110":{"good_lumis":[],"good_prescales":[],"fired":{}},"HLT_Jet80":{"good_lumis":[],"good_prescales":[],"fired":{}},
						"HLT_Jet60":{"good_lumis":[],"good_prescales":[],"fired":{}},
						"HLT_Jet30":{"good_lumis":[],"good_prescales":[],"fired":{}},"HLT_Jet300":{"good_lumis":[],"good_prescales":[],"fired":{}}}
ordered_triggers = ["HLT_Jet30","HLT_Jet60","HLT_Jet80","HLT_Jet110","HLT_Jet150","HLT_Jet190","HLT_Jet240","HLT_Jet300","HLT_Jet370"]




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
	time_series_all = []
	lumin_all = []
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
		time_series_all.append(time.mktime(dt.timetuple()))
		lumin_all.append(float(split_lines[i][6]))
		i += 1
		try:
			char = split_lines[i][0][0]
		except: pass
	return lumi_id_to_gps_times,lumi_id_to_lumin,time_series_all,lumin_all



lumi_id_to_gps_times,lumi_id_to_lumin,time_series_all,lumin_all = read_lumi_by_ls(lumibyls_file)

def get_file_trig_dict_from_txt(filepath):
	"""
	each n correponds to a different trigger name
	line n = uncut trigger name (with version)
	line n+1 = list of good lumins ids trig_dict["good_lumis"]
	line n+2 = list of good prescales trig_dict["good_prescales"]
	line n+3 = list of lumi: # times fired paired. Comes from a dict where lumi id is the key and # times fired is the value trig_dict["fired"]
				line 3 only: lumid in form run_event:#fired TAKE CARE WITH THIS+
	"""
	i = 0
	trig_dict = {}
	with open(filepath) as trig_info_file:
		for line in trig_info_file:
			line = line.splitlines()[0]
			if i % 4 == 0: # if we have a trigger name
				trigger_name = line.split()[-1] # holds for the rest of that trigger's information
				trig_dict[trigger_name] =  {
								      "good_lumis":[],
								      # corresponds to the prescale for a given GOOD LUMI BLOCK
								      "good_prescales":[],
									  "fired":{}
								     }
				
			elif i % 4 == 1: # if we have a list of good lumis:
			
				good_lumis = []
				try:
					for lumi in line.split(","):
						good_lumis.append((lumi.split(":")[0],lumi.split(":")[1]))
				except: pass
				trig_dict[trigger_name]["good_lumis"] = good_lumis
			elif i % 4 == 2: # if we have a list of prescales:
				prescales = []
				try:
					for pre in line.split(","):
						prescales.append(float(pre))
				except: pass
				trig_dict[trigger_name]["good_prescales"] = prescales
			elif i % 4 == 3:
				fired_dict = {}
				fired_info = line.split(",")
				for j in range(len(fired_info)):
					if len(fired_info[j]) != 0:	
						
						run_lumi_id = fired_info[j].split(":")[0]
						times_fired = int(fired_info[j].split(":")[1])
						fired_dict[(run_lumi_id.split("_")[0],run_lumi_id.split("_")[1])] = times_fired
				
				trig_dict[trigger_name]["fired"] = fired_dict
						
			i += 1
			
	return trig_dict
	




# for each mod file, for each trigger, get the good luminosity blocks, good prescales,
#and how many times it fired per lumi block

num_files = len(os.listdir(parsed_file_inpur_dir))
q = 1
for file in os.listdir(parsed_file_inpur_dir):
	print q, num_files
	q += 1
	file_trig_dict = get_file_trig_dict_from_txt(parsed_file_inpur_dir+"/"+file)
	for trig in file_trig_dict.keys():
		if cut_trigger_name(trig) in master_trig_dict.keys():
			for i,good_lumi in enumerate(file_trig_dict[trig]["good_lumis"]):
				if good_lumi not in master_trig_dict[cut_trigger_name(trig)]["good_lumis"]:
					master_trig_dict[cut_trigger_name(trig)]["good_lumis"].append(good_lumi)
					master_trig_dict[cut_trigger_name(trig)]["good_prescales"].append(file_trig_dict[trig]["good_prescales"][i])
					for lumi_id in file_trig_dict[trig]["fired"].keys():
						try:
							master_trig_dict[cut_trigger_name(trig)]["fired"][lumi_id] += file_trig_dict[trig]["fired"][lumi_id]
						except KeyError:
							master_trig_dict[cut_trigger_name(trig)]["fired"][lumi_id] = file_trig_dict[trig]["fired"][lumi_id]

lumi_to_events_dict = {}
for trigger in ordered_triggers:
	lumi_to_events_dict[trigger] = ([],[])
	
for trigger in ordered_triggers:
	for lumi_id in master_trig_dict[trigger]["fired"].keys():
		prescale = master_trig_dict[trigger]["good_prescales"][master_trig_dict[trigger]["good_lumis"].index(lumi_id)]
		lumi_to_events_dict[trigger][0].append(lumi_id_to_lumin[lumi_id][1]/float(prescale))
		lumi_to_events_dict[trigger][1].append(master_trig_dict[trigger]["fired"][lumi_id])

for trigger in ordered_triggers:	
	plt.figure()
	plt.scatter(lumi_to_events_dict[trigger][0],lumi_to_events_dict[trigger][1],s=1)
	plt.xlabel("Effective Luminosity")
	plt.ylabel("# fired")
	plt.title(trigger)
	plt.savefig(trigger)

	