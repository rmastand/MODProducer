# only need valid, so go through the pare py stuff. use the plot_eff_lumi stuff

import numpy as np
import sys


plot_eff_lumi_file = sys.argv[1]
lumibyls_file = sys.argv[2]
plot_eff_lumi_file = sys.argv[3]
output_file = sys.argv[4]

rev_ordered_triggers = ["HLT_Jet30","HLT_Jet60","HLT_Jet80","HLT_Jet110","HLT_Jet150","HLT_Jet190","HLT_Jet240","HLT_Jet300","HLT_Jet370"][::-1]




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
	trigger_index_dict[trigger] = np.zeros(len(runA_times))

for trig_index,trig in enumerate(rev_ordered_triggers):
	print trig
	trigger_times = np.array([float(x) for x in lines[3*trig_index+6].split(",")])
	for i,master_time in enumerate(runA_times):
		if master_time in trigger_times:
			trigger_index_dict[trigger][i] = 1

w = open(output_file,"w")
w.write()




