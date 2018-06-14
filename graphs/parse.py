import numpy as np
import datetime
import time
import sys
import ast
import os
import csv

lumibyls_file = sys.argv[1]
mod_file_inpur_dir = sys.argv[2]

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


def read_mod_file(mod_file):
	"""
	returns a dict of triggers FOR EACH MOD file
	keys are triggers names (with versions)
	subdicts are lists of good lumis the trigger was present for and the corresponding good prescale values
	"""
	trig_dict = {}

	with open(mod_file) as file:
		print "Processing file " + mod_file
		for line in file:
			# MOST CODE TAKEN FROM GET_TRIGGER_INFO.py
			# keeps track of the run, lumiBlock
			# this should signal each separate event
			if ("Cond" in line.split()) and ("#" not in line.split()):
				run,lumiBlock = line.split()[1],line.split()[3]

			if ("Trig" in line.split()) and ("#" not in line.split()):
				# all within 1 event
				# given line: [Trig identifier, trig name, prescale1, prescale2, fired?]
				if line.split()[1] not in trig_dict.keys():
					trig_dict[line.split()[1]] = {
								      "good_lumis":[],
								      # corresponds to the prescale for a given GOOD LUMI BLOCK
								      "good_prescales":[],
									  "fired":{}

								     }

					# if the lumi block is valid and if not alredy been analyzed (so present by definition)
					if is_lumi_valid((run,lumiBlock),lumi_id_to_lumin):
						if (run,lumiBlock) not in trig_dict[line.split()[1]]["good_lumis"]:
							trig_dict[line.split()[1]]["good_lumis"].append((run,lumiBlock))
							trig_dict[line.split()[1]]["good_prescales"].append(float(line.split()[2])*float(line.split()[3]))
						try:
							trig_dict[line.split()[1]]["fired"][(run,lumiBlock)]+= int(line.split()[4])
						except KeyError:
							trig_dict[line.split()[1]]["fired"][(run,lumiBlock)] = int(line.split()[4])
				else:

					if is_lumi_valid((run,lumiBlock),lumi_id_to_lumin):
						if (run,lumiBlock) not in trig_dict[line.split()[1]]["good_lumis"]:
							trig_dict[line.split()[1]]["good_lumis"].append((run,lumiBlock))
							trig_dict[line.split()[1]]["good_prescales"].append(float(line.split()[2])*float(line.split()[3]))
						try:
							trig_dict[line.split()[1]]["fired"][(run,lumiBlock)]+= int(line.split()[4])
						except KeyError:
							trig_dict[line.split()[1]]["fired"][(run,lumiBlock)] = int(line.split()[4])

		return trig_dict

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

# for each mod file, for each trigger, get the good luminosity blocks, good prescales,
#and how many times it fired per lumi block
for file in os.listdir(mod_file_inpur_dir):
	file_trig_dict = read_mod_file(mod_file_inpur_dir+"/"+file)
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
		

	# sorts all the represented lumiblocks by time, gets the integrated luminosity BY LUMI BLOCK INDEX
	ttimes,master_lumin_rec = (list(t) for t in zip(*sorted(zip(master_times,master_lumin_rec))))
	master_time_index = range(len(master_times))
	
	
	with open("graphs/plot_eff_lumin.txt", "w") as output:
		writer = csv.writer(output, lineterminator='\n')
        	writer.writerow(master_time_index)  
		writer.writerow(np.cumsum(master_lumin_rec))   

		# ordering the luminosity ids to be used as labels
		lumis_in_dispay_format = [x[0]+":"+x[1] for x in lumi_id_to_gps_times.keys()]
		ttimes,ordered_ids = (list(t) for t in zip(*sorted(zip(master_times,lumis_in_dispay_format))))
		writer.writerow(ordered_ids)   
		# for each trigger: sorts all the represented lumiblocks by time, gets the effective luminosity BY LUMI BLOCK INDEX
		for trig in ordered_triggers[::-1]:
			times,eff_lumin = (list(t) for t in zip(*sorted(zip(trigger_time_v_lumin_rec[trig][0],trigger_time_v_lumin_rec[trig][1]))))
			overlap = []
			for i,mytime in enumerate(ttimes):
				if mytime in times:
					overlap.append(master_time_index[i]) 		
			writer.writerow(overlap)  
			writer.writerow(np.cumsum(eff_lumin)) 

def plot_fired_over_eff_lumin():
	trigger_time_v_fired_lumin = {}
	for trigger in master_trig_dict.keys():
		trigger_time = []
		trigger_fired_lumin = []
		trigger_lumi = []
		for i,lumi_id in enumerate(master_trig_dict[trigger]["good_lumis"]):
			trigger_time.append(lumi_id_to_gps_times[lumi_id])
			eff_lumin = lumi_id_to_lumin[lumi_id][1]/master_trig_dict[trigger]["good_prescales"][i]
			try:
				trigger_fired_lumin.append(float(master_trig_dict[trigger]["fired"][lumi_id])/eff_lumin)
			except ZeroDivisionError:
				print eff_lumin
				print lumi_id_to_lumin[lumi_id][1],master_trig_dict[trigger]["good_prescales"][i]
			trigger_lumi.append(lumi_id[0]+":"+lumi_id[1])
		trigger_time_v_fired_lumin[trigger] = trigger_time,trigger_fired_lumin,trigger_lumi

	with open("graphs/plot_fired_over_lumin.txt", "w") as output:
		writer = csv.writer(output, lineterminator='\n')
		for trig in ordered_triggers[::-1]:
			new_times,fired_lumin = (list(t) for t in zip(*sorted(zip(trigger_time_v_fired_lumin[trig][0],trigger_time_v_fired_lumin[trig][1]))))
			new_times, ordered_ids = (list(t) for t in zip(*sorted(zip(trigger_time_v_fired_lumin[trig][0],trigger_time_v_fired_lumin[trig][2]))))
			
			writer.writerow(ordered_ids) 
			writer.writerow(range(len(fired_lumin)))  
			writer.writerow(fired_lumin) 
			
	
	
def lumi_blocks_in_file():
	
	# keys = mod files, values = dict
		# keys = lumi block id, values = counts
	lumi_blocks_in_file_dict = {}
	
	for filename in os.listdir(mod_file_inpur_dir):
		lumi_blocks_in_file_dict[filename] = {}
		with open(mod_file_inpur_dir+"/"+filename) as file:
			
			for line in file:
				if ("Cond" in line.split()) and ("#" not in line.split()):
					run,lumiBlock = line.split()[1],line.split()[3]
					try:
						lumi_blocks_in_file_dict[filename][run+"_"+lumiBlock] += 1
					except KeyError:
						lumi_blocks_in_file_dict[filename][run+"_"+lumiBlock] = 1
						
					
	
	for file in lumi_blocks_in_file_dict.keys():
		plt.figure()
		lumi_ids = lumi_blocks_in_file_dict[file].keys()
		lumi_counts = lumi_blocks_in_file_dict[file].values()
		lumi_ids,lumi_counts = (list(t) for t in zip(*sorted(zip(lumi_ids,lumi_counts))))
		print lumi_ids
		mybar = plt.bar(range(len(lumi_ids)), lumi_counts, align='center', tick_label=lumi_ids)
		for label in mybar.ax.xaxis.get_ticklabels()[::20]:
   			label.set_visible(False)
		plt.show()
		

	

plot_eff_lumin()
plot_fired_over_eff_lumin()
# currently i am NOT checking for validity for this last one
#lumi_blocks_in_file()
