"""
parses o.txt to a ready-to-plot array of numbers
"""
import numpy as np
import sys
import datetime
import time
import csv

by_event_2_file = sys.argv[1]
lumibyls_file = sys.argv[2]
output_file = sys.argv[3]
run_alumi_file = sys.argv[4]

runA_runs = []
read_alumi_lines = open(run_alumi_file,"r").readlines()
for line in read_alumi_lines[4:]:
  char = line[0]
  if char != "+":
    runA_runs.append(line.split()[1].split(":")[0])
  else:
    break
print "Done reading in ALumi"

rev_ordered_triggers = ["HLT_Jet30","HLT_Jet60","HLT_Jet80","HLT_Jet110","HLT_Jet150","HLT_Jet190","HLT_Jet240","HLT_Jet300","HLT_Jet370"][::-1]


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
	id_to_time = {}
	time_to_id = {}
	time_to_lumin = {}
	lumi_id_to_lumin = {}
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
		timestamp = time.mktime(dt.timetuple())
		lumi_id_to_lumin[(run,lumi)] = (float(split_lines[i][5]),float(split_lines[i][6]))
		id_to_time[(run,lumi)] = timestamp
		time_to_lumin[timestamp] = float(split_lines[i][6])
		time_to_id[timestamp] = run+":"+lumi
		i += 1
		try:
			char = split_lines[i][0][0]
		except: pass
	return id_to_time,time_to_lumin,lumi_id_to_lumin,time_to_id

id_to_time,time_to_lumin,lumi_id_to_lumin,time_to_id = read_lumi_by_ls(lumibyls_file)

trigger_lumi_ids_dict = {}
trigger_eff_lumis_dict = {}
trigger_eff_fired_dict = {}

i = 0
with open(by_event_2_file, "r") as input:
  for line in input:
    i += 1
    if "#" in line.split():
      trigger = line.split()[1]
      print trigger
      i = 0
    elif i == 1: # lumi ids
      lumi_ids = line.split(",")[:-1]
      lumi_ids = [(x.split(":")[0],x.split(":")[1]) for x in lumi_ids]
      trigger_lumi_ids_dict[trigger] = lumi_ids
    elif i == 2: # eff lumis
      eff_lumis = line.split(",")[:-1]
      eff_lumis = [float(x) for x in eff_lumis]
      trigger_eff_lumis_dict[trigger] = eff_lumis
    elif i == 3: # # times fired
      times_fired = line.split(",")[:-1]
      times_fired = [int(x) for x in times_fired]
      trigger_eff_fired_dict[trigger] = times_fired
 
runA_times= []
runA_lumin_rec = []
runA_ids = []

for lumi_id in lumi_id_to_lumin.keys():
		if lumi_id[0] in runA_runs:
			runA_times.append(id_to_time[lumi_id])
			runA_lumin_rec.append(lumi_id_to_lumin[lumi_id][1]) 
      			runA_ids.append(lumi_id[0]+":"+lumi_id[1])
      
print "sorting Run A"
runA_times_sorted,runA_lumin_rec_sorted = (list(t) for t in zip(*sorted(zip(runA_times,runA_lumin_rec))))
runA_times_sorted,runA_ids_sorted = (list(t) for t in zip(*sorted(zip(runA_times,runA_ids))))



output = open(output_file,"w")
writer = csv.writer(output, lineterminator='\n')

""" 
PLOT EFF LUMINOSITY AS A FUNCTION OF TIME
print out:
runA ids
runA times
runA luminosity
for each trigger, largest to smallest:
trigger times
trigger luminosity
"""
print "eff lumi as time" 
writer.writerow(runA_ids_sorted)  
writer.writerow(runA_times_sorted)  
writer.writerow(runA_lumin_rec_sorted)  


for trigger in rev_ordered_triggers[::-1]:
  # write the times out
  trigger_times = [id_to_time[lumi_id] for x in trigger_lumi_ids_dict[trigger]]
  trigger_times_sorted,trigger_lumin_rec_sorted = (list(t) for t in zip(*sorted(zip(trigger_times,trigger_eff_lumis_dict[trigger]))))
  writer.writerow(trigger_times_sorted)  
  writer.writerow(trigger_lumin_rec_sorted)  

  
""" 
PLOT EFF LUMINOSITY AS THE LUMI ID
print out:
runA ids
runA ids nums
runA luminosity
for each trigger, largest to smallest:
trigger ids nums
trigger luminosity
"""
print "eff lumi as id" 
master_id_nums = range(len(runA_ids_sorted))
  
writer.writerow(runA_ids_sorted)  
writer.writerow(master_id_nums)  
writer.writerow(runA_lumin_rec_sorted)  

for trigger in rev_ordered_triggers[::-1]:
  trigger_times = [id_to_time[lumi_id] for x in trigger_lumi_ids_dict[trigger]]
  trigger_ids = []
  for id,time in enumerate(runA_times_sorted):
    if time in trigger_times:
      trigger_ids.append(id)
  writer.writerow(trigger_ids)  
  writer.writerow(trigger_lumin_rec_sorted)  
  


""" 
PLOT CROSS SECTION AS THE TIMES
print out:
for each trigger, largest to smallest:
trigger ids times
trigger luminosity
"""
print "cross lumsection as time" 
for trigger in rev_ordered_triggers[::-1]:
  trigger_times = [id_to_time[lumi_id] for x in trigger_lumi_ids_dict[trigger]]
  trigger_cross_section = []
  for i,eff_lumin in enumerate(trigger_eff_lumis_dict[trigger]):
    trigger_cross_section.append(float(eff_lumin)/trigger_eff_fired_dict[trigger])
  trigger_times_sorted,trigger_cross_section_sorted = (list(t) for t in zip(*sorted(zip(trigger_times,trigger_cross_section))))
  writer.writerow(trigger_times_sorted)  
  writer.writerow(trigger_cross_section_sorted)  
  
""" 
PLOT CROSS SECTION AS THE IDS
print out:
for each trigger, largest to smallest:
trigger ids nums
trigger luminosity
"""
print "cross section as id" 
for trigger in rev_ordered_triggers[::-1]:
  trigger_times = [id_to_time[lumi_id] for x in trigger_lumi_ids_dict[trigger]]
  trigger_ids = []
  for id,time in enumerate(runA_times_sorted):
    if times in trigger_times:
      trigger_ids.append(id)
  trigger_cross_section = []
  for i,eff_lumin in enumerate(trigger_eff_lumis_dict[trigger]):
    trigger_cross_section.append(float(eff_lumin)/trigger_eff_fired_dict[trigger])
  writer.writerow(trigger_ids)  
  writer.writerow(trigger_cross_section_sorted)  
  

 
