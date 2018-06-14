import numpy as np
import sys
import os
import csv

parsed_file_inpur_dir = sys.argv[1]


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
			line = line.strip()
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
					print fired_info[j]
					
					run_lumi_id = fired_info[j].split(":")[0]
					times_fired = int(fired_info[j].split(":")[1].replace("\n",""))
					fired_dict[(run_lumi_id.split("_")[0],run_lumi_id.split("_")[1])] = times_fired
				trig_dict[trigger_name]["fired"] = fired_dict
						
			i += 1
			
	return trig_dict
	




# for each mod file, for each trigger, get the good luminosity blocks, good prescales,
#and how many times it fired per lumi block
l = 0
for file in os.listdir(parsed_file_inpur_dir):
	if l == 0:
		file_trig_dict = get_file_trig_dict_from_txt(parsed_file_inpur_dir+"/"+file)
		
	l += 1

for trig in file_trig_dict.keys():
	print trig
	print
	print
	print file_trig_dict[trig]["good_lumis"]
	print
	print
	print file_trig_dict[trig]["good_prescales"]
	print
	print
	
	"""
	for trig in file_trig_dict.keys():
		if cut_trigger_name(trig) in master_trig_dict.keys():
			master_trig_dict[cut_trigger_name(trig)]["good_lumis"] = master_trig_dict[cut_trigger_name(trig)]["good_lumis"]+file_trig_dict[trig]["good_lumis"]
			master_trig_dict[cut_trigger_name(trig)]["good_prescales"] = master_trig_dict[cut_trigger_name(trig)]["good_prescales"]+file_trig_dict[trig]["good_prescales"]
			for lumi_id in file_trig_dict[trig]["fired"].keys():
				try:
					master_trig_dict[cut_trigger_name(trig)]["fired"][lumi_id] += file_trig_dict[trig]["fired"][lumi_id]
				except KeyError:
					master_trig_dict[cut_trigger_name(trig)]["fired"][lumi_id] = file_trig_dict[trig]["fired"][lumi_id]
	"""

"""
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
			print eff_lumin
			print lumi_id_to_lumin[lumi_id][1]
			trigger_fired_lumin.append(float(master_trig_dict[trigger]["fired"][lumi_id])/eff_lumin)
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
"""
