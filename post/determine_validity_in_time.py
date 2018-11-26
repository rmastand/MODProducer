# only need valid, so go through the pare py stuff. use the plot_eff_lumi stuff

import numpy as np
import sys
import datetime
import time


plot_eff_lumi_file = sys.argv[1]
lumibyls_file = sys.argv[3]


rev_ordered_triggers = ["HLT_Jet30","HLT_Jet60","HLT_Jet80","HLT_Jet110","HLT_Jet150","HLT_Jet190","HLT_Jet240","HLT_Jet300","HLT_Jet370"][::-1]


def lumi_id_to_dmy(lumibyls_file):
	"""
	returns two dicts with keys = (run,lumiBlock)
	1st values: gps times
	2nd values: (lumi_delivered, lumi_recorded)
	"""
	lumibyls = open(lumibyls_file)
	lines =  lumibyls.readlines()
	split_lines = [line.split(",") for line in lines][2:]
	char = ""
	lumi_id_to_date = {}
	i = 0
	while char !="#":
		run = split_lines[i][0].split(":")[0]
		lumi = split_lines[i][1].split(":")[0]
		date = split_lines[i][2].split(" ")[0]
		tim = split_lines[i][2].split(" ")[1]
		mdy = [int(x) for x in date.split("/")]
		hms = [int(x) for x in tim.split(":")]
		dt = datetime.datetime(mdy[2], mdy[0], mdy[1], hms[0], hms[1],hms[2])
		lumi_id_to_date[(run,lumi)] = str(mdy[1])+"/"+str(mdy[0])+"/"+str(mdy[2])
		i += 1
		try:
			char = split_lines[i][0][0]
		except: pass
	return lumi_id_to_date
lumi_id_to_date = lumi_id_to_dmy(lumibyls_file)



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
runA_times = np.array([float(x) for x in lines[1].split(",")])
runA_index = np.array(range(len(runA_lumin)))+1
master_index = np.array([int(x) for x in lines[3].split(",")])+1
master_lumin = np.array([float(x) for x in lines[4].split(",")])
time_ordered_lumi_id = lines[5].split(",")

#print np.logspace(min(master_index),max(master_index),num_samples)
good_indices = np.logspace(np.log10(min(runA_index)),np.log10(max(runA_index)),num_samples).astype(int) -min(runA_index)

plt.plot(np.take(runA_index,good_indices),np.take(runA_lumin,good_indices),"k",linewidth=9.0)



for trig_index,trig in enumerate(rev_ordered_triggers):
	print trig

	index = np.array([int(x) for x in lines[3*trig_index+7].split(",")])+1

	eff_lumin = np.array([float(x) for x in lines[3*trig_index+8].split(",")])
	good_indices = np.logspace(np.log10(min(index)),np.log10(max(index)),num_samples).astype(int) - min(index)
	print len(index), len(eff_lumin)

        



graph_eff_lumin()
graph_eff_lumin_time_ordered()

