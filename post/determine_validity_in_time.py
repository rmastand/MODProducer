# only need valid, so go through the pare py stuff. use the plot_eff_lumi stuff

import numpy as np
import sys


plot_eff_lumi_file = sys.argv[1]
lumibyls_file = sys.argv[2]
output_file = sys.argv[3]

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
	lumi_id_to_gps_times = {}
	lumi_id_to_lumin = {}
	time_series_all = []
	lumin_all = []
	i = 0
	while char !="#":
		run = split_lines[i][0].split(":")[0]
		lumi = split_lines[i][1].split(":")[0]	
		lumi_id = run+":"+lumi
		lumi_id_to_lumin[lumi_id] = (float(split_lines[i][5]),float(split_lines[i][6]))

		i += 1
		try:
			char = split_lines[i][0][0]
		except: pass
	return lumi_id_to_lumin



lumi_id_to_lumin = read_lumi_by_ls(lumibyls_file)


"""
plot_eff_luminosity.txt:
Total Integrated Luminosity, number index
Total Integrated Luminosity, cumsum value
Time ordered luminosity ids for all represented lumiblocks (use for x axis labels)
For each trigger, going from BIGGEST TO SMALLEST:
Effective Luminosity, number index
Effective Luminosity, cumsum value
"""

eff_lumi_file =  open(plot_eff_lumi_file)
lines = eff_lumi_file.readlines()
# for the total luminosity file:

# all point represent VALID lumiblocks, either in totla or for a given trigger
runA_times = np.array([float(x) for x in lines[0].split(",")])
time_ordered_lumi_id = lines[5].split(",")

trigger_index_dict = {}

for trigger in rev_ordered_triggers:
	trigger_index_dict[trigger] = []

for trig_index,trigger in enumerate(rev_ordered_triggers):
	trigger_times = np.array([float(x) for x in lines[3*trig_index+6].split(",")])
	for i,master_time in enumerate(runA_times):
		if master_time in trigger_times:
			trigger_index_dict[trigger].append("1")
		else:
			trigger_index_dict[trigger].append("0")

n = 15
w = open(output_file,"w")

first_line = setw("Time",n)
for trigger in rev_ordered_triggers:
	first_line += " " + setw(trigger,n)
w.write(first_line+"\n")

zero_events_times = []
zero_events_lumis = []
zero_events_lumin = []
for i,master_time in enumerate(runA_times):
	test_sum = 0
	if i % 10000 == 0:
		print i, len(runA_times)
	line = setw(str(master_time),n)
	
	for trigger in rev_ordered_triggers:
		test_sum+= int(trigger_index_dict[trigger][i])
		
		line += " " + setw(trigger_index_dict[trigger][i],n)
	w.write(line+"\n")
	if test_sum == 0:
		zero_events_times.append(master_time)
		zero_events_lumis.append(time_ordered_lumi_id[i])
		zero_events_lumin.append(lumi_id_to_lumin[time_ordered_lumi_id[i]])
		

w.close()

print zero_events_times
print zero_events_lumis
print zero_events_lumin
print len(zero_events_times)

print "finished writing"

print "total valid lumi in run A", len(runA_times)


for trigger in rev_ordered_triggers:
	array = trigger_index_dict[trigger]
	print "total valid in ", trigger, sum([float(x) for x in array])
"""
	
print "testing 101"
search_val = ["1","0","1"]
N = len(search_val)
for trigger in rev_ordered_triggers:
	array = trigger_index_dict[trigger]
	possibles = np.where(array == search_val[0])[0]
	solns = []
	for p in possibles:
    		check = values[p:p+N]
    		if np.all(check == searchval):
       			solns.append(p)
	print(solns)
	
print "testing 1001"
search_val = ["1","0","0","1"]
N = len(search_val)
for trigger in rev_ordered_triggers:
	array = trigger_index_dict[trigger]
	possibles = np.where(array == search_val[0])[0]
	solns = []
	for p in possibles:
    		check = values[p:p+N]
    		if np.all(check == searchval):
       			solns.append(p)
	print(solns)
	

print "testing 10001"
search_val = ["1","0","0","0","1"]
N = len(search_val)
for trigger in rev_ordered_triggers:
	array = trigger_index_dict[trigger]
	possibles = np.where(array == search_val[0])[0]
	solns = []
	for p in possibles:
    		check = values[p:p+N]
    		if np.all(check == searchval):
       			solns.append(p)
	print(solns)
	
"""





