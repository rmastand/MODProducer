import numpy as np
import sys
import os
import datetime
import time
import csv

parsed_file_inpur_dir = sys.argv[1]
lumibyls_file = sys.argv[2]
run_alumi_file = sys.argv[3]
output_file = sys.argv[4]

runA_runs = []
read_alumi_lines = open(run_alumi_file,"r").readlines()
for line in read_alumi_lines[4:]:
  char = line[0]
  if char != "+":
    runA_runs.append(line.split()[1].split(":")[0])
  else:
    break
print "Done reading in ALumi"


def setw(word,n):
	return " "*(n-len(word))+word


def cut_trigger_name(name):
	"""removes the version number from the trigger names"""
	return name.rsplit("_", 1)[0]

# good_lumis,good_prescales
#master_trig_dict = {"HLT_Jet190":{"good_lumis":[],"good_prescales":[],"fired":{}},"HLT_Jet370":{"good_lumis":[],"good_prescales":[],"fired":{}},
#					"HLT_Jet150":{"good_lumis":[],"good_prescales":[],"fired":{}},"HLT_Jet240":{"good_lumis":[],"good_prescales":[],"fired":{}},
#					"HLT_Jet110":{"good_lumis":[],"good_prescales":[],"fired":{}},"HLT_Jet80":{"good_lumis":[],"good_prescales":[],"fired":{}},
#						"HLT_Jet60":{"good_lumis":[],"good_prescales":[],"fired":{}},
#						"HLT_Jet30":{"good_lumis":[],"good_prescales":[],"fired":{}},"HLT_Jet300":{"good_lumis":[],"good_prescales":[],"fired":{}}}
#ordered_triggers = ["HLT_Jet30","HLT_Jet60","HLT_Jet80","HLT_Jet110","HLT_Jet150","HLT_Jet190","HLT_Jet240","HLT_Jet300","HLT_Jet370"]

master_trig_dict ={}


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



lumi_id_to_gps_times,lumi_id_to_lumin = read_lumi_by_ls(lumibyls_file)

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
				master_trig_dict[trigger_name[:-3]] = {
								      "good_lumis":[],
								      # corresponds to the prescale for a given GOOD LUMI BLOCK
								      "good_prescales":[],
									  "fired":{}
								     }
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
		if cut_trigger_name(trig) not in master_trig_dict.keys():
			master_trig_dict[cut_trigger_name(trig)] = {"good_lumis":[],"good_prescales":[]}
		for i,good_lumi in enumerate(file_trig_dict[trig]["good_lumis"]):
			if good_lumi not in master_trig_dict[cut_trigger_name(trig)]["good_lumis"]:
				master_trig_dict[cut_trigger_name(trig)]["good_lumis"].append(good_lumi)
				master_trig_dict[cut_trigger_name(trig)]["good_prescales"].append(file_trig_dict[trig]["good_prescales"][i])



					
					
					
					
def write_eff_lumin_and_prescales():
	# finds time vs effective luminosity curves for all triggers
	trigger_time_v_lumin_rec = {}
	# also finds the integrated luminosity for all represented lumiblocks
	master_lumin_ids = []
	for trigger in master_trig_dict.keys():
		print trigger
		trigger_time = []
		trigger_eff_lumin = []
		for i,lumi_id in enumerate(master_trig_dict[trigger]["good_lumis"]):
			if lumi_id not in master_lumin_ids:
				master_lumin_ids.append(lumi_id)
			trigger_time.append(lumi_id_to_gps_times[lumi_id])
			trigger_eff_lumin.append(lumi_id_to_lumin[lumi_id][1]/master_trig_dict[trigger]["good_prescales"][i])
		trigger_time_v_lumin_rec[trigger] = trigger_time,trigger_eff_lumin

	# now to get the time / recorded integrated luminosity data
	master_times = []
	master_lumin_rec = []
	
	runA_times= []
	runA_lumin_rec = []
	
	for lumi_id in master_lumin_ids:
		master_times.append(lumi_id_to_gps_times[lumi_id])
		master_lumin_rec.append(lumi_id_to_lumin[lumi_id][1]) 
	
	for lumi_id in lumi_id_to_lumin.keys():
		if lumi_id[0] in runA_runs:
			runA_times.append(lumi_id_to_gps_times[lumi_id])
			runA_lumin_rec.append(lumi_id_to_lumin[lumi_id][1]) 
	
	
	print "start sorting"
	# sorts all the represented lumiblocks by time, gets the integrated luminosity BY LUMI BLOCK INDEX
	master_times_sorted,master_lumin_rec = (list(t) for t in zip(*sorted(zip(master_times,master_lumin_rec))))
	print "done sorting"

	

	
	
	with open(output_file, "w") as output:
		
		output.write(setw("Total luminosity",40)+setw(str(np.sum(runA_lumin_rec))[:30],40)+"\n")
		
		# ordering the luminosity ids to be used as labels
		
		output.write(setw("Trigger Name",40)+setw("Eff Lumin Rec",30)+setw("Avg Prescale",30)+"\n")
		
		# for each trigger: sorts all the represented lumiblocks by time, gets the effective luminosity BY LUMI BLOCK INDEX
		for trig in master_trig_dict.keys():
			
			
			times,eff_lumin = (list(t) for t in zip(*sorted(zip(trigger_time_v_lumin_rec[trig][0],trigger_time_v_lumin_rec[trig][1]))))

			eff_lumin_2 = []
			for i,mytime in enumerate(master_times_sorted):
				if mytime in times:

					eff_lumin_2.append(eff_lumin[times.index(mytime)])
			print len(eff_lumin_2),len(eff_lumin)
			output.write(setw(trig,40)+setw(str(np.sum(eff_lumin_2))[:25],30)+setw(str(np.mean(master_trig_dict[trig]["good_prescales"]))[:25],30)+"\n")

			print "going"

	
			
		

write_eff_lumin_and_prescales()
# currently i am NOT checking for validity for this last one
#lumi_blocks_in_file()

