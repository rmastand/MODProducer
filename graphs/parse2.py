import numpy as np
import sys
import os
import datetime
import time
import csv

parsed_file_inpur_dir = sys.argv[1]
lumibyls_file = sys.argv[2]


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
			master_trig_dict[cut_trigger_name(trig)]["good_lumis"] = master_trig_dict[cut_trigger_name(trig)]["good_lumis"]+file_trig_dict[trig]["good_lumis"]
			master_trig_dict[cut_trigger_name(trig)]["good_prescales"] = master_trig_dict[cut_trigger_name(trig)]["good_prescales"]+file_trig_dict[trig]["good_prescales"]
			for lumi_id in file_trig_dict[trig]["fired"].keys():
				try:
					master_trig_dict[cut_trigger_name(trig)]["fired"][lumi_id] += file_trig_dict[trig]["fired"][lumi_id]
				except KeyError:
					master_trig_dict[cut_trigger_name(trig)]["fired"][lumi_id] = file_trig_dict[trig]["fired"][lumi_id]


def plot_eff_lumin():
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
	for lumi_id in master_lumin_ids:
		master_times.append(lumi_id_to_gps_times[lumi_id])
		master_lumin_rec.append(lumi_id_to_lumin[lumi_id][1]) 
		
	print "start sorting"
	# sorts all the represented lumiblocks by time, gets the integrated luminosity BY LUMI BLOCK INDEX
	master_times_sorted,master_lumin_rec = (list(t) for t in zip(*sorted(zip(master_times,master_lumin_rec))))
	print "done sorting"
	
	
	
	with open("graphs/plot_eff_lumin.txt", "w") as output:
		writer = csv.writer(output, lineterminator='\n')
        	writer.writerow(master_times_sorted)  
		master_times_index = range(len(master_times_sorted))
		writer.writerow(master_times_index)   
		writer.writerow(np.cumsum(master_lumin_rec))   
	

		# ordering the luminosity ids to be used as labels
		times_sorted,ordered_ids = (list(t) for t in zip(*sorted(zip(master_times,master_lumin_ids))))
		writer.writerow(ordered_ids)   
		# for each trigger: sorts all the represented lumiblocks by time, gets the effective luminosity BY LUMI BLOCK INDEX
		for trig in ordered_triggers[::-1]:
			times,eff_lumin = (list(t) for t in zip(*sorted(zip(trigger_time_v_lumin_rec[trig][0],trigger_time_v_lumin_rec[trig][1]))))
			overlap_times = []
			overlap_index = []
			for i,mytime in enumerate(times_sorted):
				if mytime in times:
					overlap_times.append(master_times_sorted[i]) 	
					overlap_index.append(master_times_index[i]) 
			writer.writerow(overlap_times)  
			writer.writerow(overlap_index)  
			writer.writerow(np.cumsum(eff_lumin)) 
			print "going"

	return ttimes,master_time_index,master_times_sorted

def plot_fired_over_eff_lumin(ttimes,master_time_index,master_times_sorted):
	trigger_time_v_fired_lumin = {}
	for trigger in master_trig_dict.keys():
		trigger_time = []
		trigger_fired_lumin = []
		trigger_lumi = []
		for i,lumi_id in enumerate(master_trig_dict[trigger]["good_lumis"]):
			eff_lumin = lumi_id_to_lumin[lumi_id][1]/master_trig_dict[trigger]["good_prescales"][i]
			try:
				trigger_fired_lumin.append(float(master_trig_dict[trigger]["fired"][lumi_id])/eff_lumin)
				trigger_time.append(lumi_id_to_gps_times[lumi_id])
				trigger_lumi.append(lumi_id[0]+":"+lumi_id[1])
			except ZeroDivisionError:
				pass
		trigger_time_v_fired_lumin[trigger] = trigger_time,trigger_fired_lumin,trigger_lumi

	with open("graphs/plot_fired_over_lumin.txt", "w") as output:
		writer = csv.writer(output, lineterminator='\n')
		for trig in ordered_triggers[::-1]:
			new_times,fired_lumin = (list(t) for t in zip(*sorted(zip(trigger_time_v_fired_lumin[trig][0],trigger_time_v_fired_lumin[trig][1]))))
			new_times, ordered_ids = (list(t) for t in zip(*sorted(zip(trigger_time_v_fired_lumin[trig][0],trigger_time_v_fired_lumin[trig][2]))))
			
			overlap_index = []
			overlap_time = []
			for i,mytime in enumerate(ttimes):
				if mytime in new_times:
					overlap_index.append(master_time_index[i]) 
					overlap_time.append(master_times_sorted[i])
					
			
			writer.writerow(ordered_ids) 
			writer.writerow(overlap_time)  
			writer.writerow(overlap_index)  
			writer.writerow(fired_lumin) 
			print "going2"
	
			
	
	

	

ttimes,master_time_index,master_times_sorted = plot_eff_lumin()
plot_fired_over_eff_lumin(ttimes,master_time_index,master_times_sorted)
# currently i am NOT checking for validity for this last one
#lumi_blocks_in_file()

