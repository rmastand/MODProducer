"""
A script to make a table of the triggers -- who could have guessed??
"""

import sys
import os
import numpy as np

eff_lumin_table = sys.argv[1]
table_out_name = sys.argv[2]
setting = sys.argv[3]
lumi_dir = sys.argv[4]


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

valid_lumi_runA = 109428.
											
triggers_lumin_eff_dict	= {}				
lumi_info_file = open(eff_lumin_table,"r")

read_lines = lumi_info_file.readlines()
total_luminosity = float(read_lines[0].split()[2])
for line in read_lines[2:]:
	trigger_name = line.split()[0]
	eff_lumin_rec = line.split()[1]
	avg_prescale = line.split()[2]
	triggers_lumin_eff_dict[trigger_name] = (eff_lumin_rec,avg_prescale)
	
# trigger: (total, valid)
valid_lumi_dict = {}

for file in os.listdir(lumi_dir):
	with open(lumi_dir+"/"+file, "r") as lumi_file:
		for line in lumi_file:
			trigger = line.split()[0][:-3]
			print trigger
			total = int(line.split()[1])
			valid = int(line.split()[2])
			try:
				valid_lumi_dict[trigger][0] += total
				valid_lumi_dict[trigger][1] += valid
			except:
				valid_lumi_dict[trigger] = [total,valid]

											
def setw(word,n):
	return " "*(n-len(word))+word
			
n = 15
w = open(table_out_name,"w")
if setting == "event":
	w.write(setw("Trigger Name",35)  + setw("Present",n)+ setw("Frac Present",n)+setw("Valid",n)+ setw("Frac Valid",n) + setw("Fired",n)+ setw("Frac Fired",n)+setw("Eff Lumi Rec",20)+setw("Avg Prescale",20) +"\n") 

	for trigger_name in all_triggers_dict.keys():	
		w.write(setw(trigger_name,35)+setw(str(all_triggers_dict[trigger_name][0]),n)+setw( str(float(all_triggers_dict[trigger_name][0])/float(total_events[0]))[:10],n)+setw(str(all_triggers_dict[trigger_name][1]),n)+setw( str(float(all_triggers_dict[trigger_name][1])/float(total_events[0]))[:10],n)  +setw(str(all_triggers_dict[trigger_name][2]),n)+setw( str(float(all_triggers_dict[trigger_name][2])/float(total_events[0]))[:10],n)+setw(triggers_lumin_eff_dict[trigger_name][0],20)+setw(str(total_luminosity/float(triggers_lumin_eff_dict[trigger_name][0])),20)  + "\n") 

	w.write(setw("Total",35)+setw(str(total_events[0]),n)+setw("1",n)+setw(str(total_events[1]),n)+setw(str(float(total_events[1])/float(total_events[0]))[:10],n)  +setw("N/A",n)+setw("N/A",n)+setw(str(total_luminosity),20)+setw("NA",20)  + "\n") 
if setting == "lumi":
	w.write(setw("Trigger Name",35)  + setw("Present",n)+ setw("Frac Present",n)+setw("Valid",n)+ setw("Frac Valid",n) +setw("Eff Lumi Rec",20)+setw("Avg Prescale",20) +"\n") 

	for trigger_name in all_triggers_dict.keys():	
		w.write(setw(trigger_name,35)+
			setw(str(valid_lumi_dict[trigger][0]]),n)+setw( str(valid_lumi_dict[trigger][0]]/valid_lumi_runA),n)+setw(str(valid_lumi_dict[trigger][1] ),n)+setw( str(valid_lumi_dict[trigger][1]]/valid_lumi_runA),n)  +setw(triggers_lumin_eff_dict[trigger_name][0],20)+setw(str(total_luminosity/float(triggers_lumin_eff_dict[trigger_name][0])),20)  + "\n") 

	w.write(setw("Total",35)+setw("N/A",n)+setw("N/A",n)+setw(str(valid_lumi_runA),n)+setw("1",n)  +setw(str(total_luminosity),20)+setw("NA",20)  + "\n") 

	
w.close()


