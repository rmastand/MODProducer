# only need valid, so go through the pare py stuff. use the plot_eff_lumi stuff

import numpy as np
import sys


plot_eff_lumi_file = sys.argv[1]
lumibyls_file = sys.argv[2]
output_file = sys.argv[3]

rev_ordered_triggers = ["HLT_Jet30","HLT_Jet60","HLT_Jet80","HLT_Jet110","HLT_Jet150","HLT_Jet190","HLT_Jet240","HLT_Jet300","HLT_Jet370"][::-1]

def setw(word,n):
	return " "*(n-len(word))+word


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

for i,master_time in enumerate(runA_times):
	if i % 10000 == 0:
		print i, len(runA_times)
	line = setw(str(master_time),n)
	
	for trigger in rev_ordered_triggers:
		
		line += " " + setw(trigger_index_dict[trigger][i],n)
	w.write(line+"\n")

w.close()

print "finished writing"

search_val = ["1","0","1"]
for trigger in rev_ordered_triggers:
	print trigger
	array = trigger_index_dict[trigger]
	idx = [np.s_[i:m-n+1+i] for i in range(n)]
	found = [array[idx[i]] == search_val[i] for i in range(n)]
	found_1 = np.all(found, axis=0)
	print np.where(found_1)


