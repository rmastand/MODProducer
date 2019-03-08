# only need valid, so go through the pare py stuff. use the plot_eff_lumi stuff

import numpy as np
import sys
import datetime
import time


by_event_2_file = sys.argv[1]
lumibyls_file = sys.argv[2]
output_file = sys.argv[3]
summary_file = sys.argv[4]
run_alumi_file = sys.argv[5]


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

def setw(word,n):
	return " "*(n-len(word))+word

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
	time_to_lumin_del = {}
	time_to_lumin_rec = {}
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
		time_to_lumin_rec[timestamp] = float(split_lines[i][6])
		time_to_lumin_del[timestamp]= float(split_lines[i][5])
		time_to_id[timestamp] = run+":"+lumi
		i += 1
		try:
			char = split_lines[i][0][0]
		except: pass
	return id_to_time,time_to_lumin_del,time_to_lumin_rec,lumi_id_to_lumin,time_to_id






id_to_time,time_to_lumin_del,time_to_lumin_rec,lumi_id_to_lumin,time_to_id = read_lumi_by_ls(lumibyls_file)




"""
plot_eff_luminosity.txt:
Total Integrated Luminosity, number index
Total Integrated Luminosity, cumsum value
Time ordered luminosity ids for all represented lumiblocks (use for x axis labels)
For each trigger, going from BIGGEST TO SMALLEST:
Effective Luminosity, number index
Effective Luminosity, cumsum value
"""
j = 0
trigger_ids_dict = {}
i = 0
with open(by_event_2_file, "r") as input:
  for line in input:
    j += 1
    i += 1
    if "#" in line.split():
      trigger = line.split()[1]
      print trigger
      i = 0
    elif i == 1: # lumi ids
      lumi_ids = line.split(",")[:-1]
      lumi_ids = [(x.split(":")[0],x.split(":")[1]) for x in lumi_ids]
      trigger_ids_dict[trigger] = lumi_ids
    elif i == 2: # eff lumis
      pass
    elif i == 3: # # times fired
      pass
print j

for trigger in trigger_ids_dict.keys():
	print trigger
	print len(trigger_ids_dict[trigger])
print "done reading file"
# all point represent VALID lumiblocks, either in totla or for a given trigger
runA_times= []
for lumi_id in lumi_id_to_lumin.keys():
		if lumi_id[0] in runA_runs:
			runA_times.append(id_to_time[lumi_id])
print len(runA_times)
runA_times = sorted(runA_times)	


			
trigger_index_dict = {}

for trigger in rev_ordered_triggers:
	trigger_index_dict[trigger] = []

for trig_index,trigger in enumerate(rev_ordered_triggers):
	print trigger
	trigger_ids = trigger_ids_dict[trigger]
	trigger_times = [id_to_time[x] for x in trigger_ids]
	for i,master_time in enumerate(runA_times):
		if master_time in trigger_times:
			trigger_index_dict[trigger].append("1")
		else:
			trigger_index_dict[trigger].append("0")

n = 15
w = open(output_file,"w")
s = open(summary_file,"w")

first_line = setw("Time",n)
for trigger in rev_ordered_triggers:
	first_line += " " + setw(trigger,n)
w.write(first_line+"\n")

n = 15
first_line = setw("Event time",n) + setw("Event ID",n) +setw("EventLumiDel",n)+setw("EventLumiRec",n) +setw("Pre time",n) +setw("Pre ID",n) +setw("PreLumiDel",n)+setw("PreLumiRec",n)  +setw("Post time",n) +setw("Post ID",n) +setw("PostLumiDel",n)+setw("PostLumiRec",n) 

s.write(first_line+"\n")





zero_events_times = []
zero_events_lumis = []
zero_events_lumin = []
for i,master_time in enumerate(runA_times):
	
	event_time = master_time
	event_id = time_to_id[event_time]	
	event_lumin_del = time_to_lumin_del[event_time]
	event_lumin_rec = time_to_lumin_rec[event_time]
	try: 
		prev_time = runA_times[i-1]
	except IndexError:
		prev_time = "N/A"
	try: 
		post_time = runA_times[i+1]
	except IndexError:
		post_time = "N/A"
		
	test_sum = 0
	if i % 10000 == 0:
		print i, len(runA_times)
	line = setw(str(master_time),n)
	
	for trigger in rev_ordered_triggers:
		test_sum+= int(trigger_index_dict[trigger][i])
		
		line += " " + setw(trigger_index_dict[trigger][i],n)
	w.write(line+"\n")
	if test_sum == 0:
		zero_events_times.append(event_time)
		zero_events_lumis.append(event_id)
		zero_events_lumin.append(event_lumin_rec)
		try: prev_id = time_to_id[prev_time]	
		except KeyError: prev_id = "N/A"
		try: post_id = time_to_id[post_time]	
		except KeyError: prev_id = "N/A"
		try: 
			prev_lumin_del = time_to_lumin_del[prev_time]	
			prev_lumin_rec = time_to_lumin_rec[prev_time]	
		except KeyError: prev_id = "N/A"
		try: 
			post_lumin_del = time_to_lumin_del[post_time]	
			post_lumin_rec = time_to_lumin_rec[post_time]	
		except KeyError: prev_id = "N/A"
			
		line  = setw(str(event_time),n) + setw(str(event_id),n) +setw(str(event_lumin_del),n)+setw(str(event_lumin_rec),n) +setw(str(prev_time),n) +setw(str(prev_id),n) +setw(str(prev_lumin_del),n) +setw(str(prev_lumin_rec),n) +setw(str(post_time),n) +setw(str(post_id),n) +setw(str(post_lumin_del),n)+setw(str(post_lumin_rec),n)  
		s.write(line+"\n")
		

w.close()
s.close()

print zero_events_times
print zero_events_lumis
print zero_events_lumin
print len(zero_events_times)

print "finished writing"

print "total valid lumi in run A", len(runA_times)


for trigger in rev_ordered_triggers:
	array = trigger_index_dict[trigger]
	print "total valid in ", trigger, sum([float(x) for x in array])





