"""
A script to make a table of the triggers -- who could have guessed??
"""

import sys
import os
import numpy as np



all_trig_dirs = ["/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/trig/12Oct2013-v1/10000/",
"/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/trig/12Oct2013-v1/20000_a/",
"/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/trig/12Oct2013-v1/20000_b/",
"/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/trig/12Oct2013-v1/20000_c/",
"/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/trig/12Oct2013-v1/20001/"]

#structure: trigger: (present,valid,fired)
#contains a bonus item: total events = (present, valid)
total_events  = [0,0]
all_triggers_dict = {}

for trig_dir in all_trig_dirs:
	for file in os.listdir(trig_dir):
		with open(trig_dir+"/"+file, "r") as trig_file:
			for line in trig_file:
				if ("File" in line.split()) and ("#" not in line.split()):
					
					total_events[0] += int(line.split()[2])
					total_events[1] += int(line.split()[3])
				# looks for each trigger event
				if ("Trig" in line.split()) and ("#" not in line.split()):
					master_info = line.split()
					#ignore the version numbers for the trigger name
					trigger_name = master_info[1][:-3]
					present = int(master_info[2])
					valid = int(master_info[3])
					fired = int(master_info[4])

					# if we haven't seen the trigger before:
					if trigger_name not in all_triggers_dict.keys():
						all_triggers_dict[trigger_name] = [present, valid, fired]
					else:
						all_triggers_dict[trigger_name][0] += present
						all_triggers_dict[trigger_name][1] += valid
						all_triggers_dict[trigger_name][2] += fired

def setw(word,n):
	return " "*(n-len(word))+word
			
n = 20
w = open("trigger_table.txt","w")
w.write("total events:"+str(total_events[0])+", valid events:"+str(total_events[1])+"\n")
w.write(setw("Trigger Name",35)  + setw("Present",n)+ setw("Frac Present",n)+setw("Valid",n)+ setw("Frac Valid",n) + setw("Fired",n)+ setw("Frac Fired",n) +"\n") 

for trigger_name in all_triggers_dict.keys():
	
	
	w.write(setw(trigger_name,35)+setw(str(all_triggers_dict[trigger_name][0]),n)+setw("1",n)+setw(str(all_triggers_dict[trigger_name][1]),n)+setw( str(float(all_triggers_dict[trigger_name][1])/float(all_triggers_dict[trigger_name][0]))[:10],n)  +setw(str(all_triggers_dict[trigger_name][2]),n)+setw( str(float(all_triggers_dict[trigger_name][2])/float(all_triggers_dict[trigger_name][0]))[:10],n)  + "\n") 
w.close()


