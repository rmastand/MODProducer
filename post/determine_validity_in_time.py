
import numpy as np
import sys
import csv


run_alumi_file = sys.argv[1]
lumibyls_file = sys.argv[2]

# first: order all the lumiblocks in run A. they should be already ordered in this file
runA_runs = []
read_alumi_lines = open(run_alumi_file,"r").readlines()
for line in read_alumi_lines[4:]:
  char = line[0]
  if char != "+":
    runA_runs.append(line.split()[1].split(":")[0])
  else:
    break
print "Done reading in ALumi"

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
		date = split_lines[i][2].split(" ")[0]
		tim = split_lines[i][2].split(" ")[1]
		mdy = [int(x) for x in date.split("/")]
		hms = [int(x) for x in tim.split(":")]
		dt = datetime.datetime(mdy[2], mdy[0], mdy[1], hms[0], hms[1],hms[2])
		lumi_id_to_gps_times[(run,lumi)] = time.mktime(dt.timetuple())
		lumi_id_to_lumin[(run,lumi)] = (float(split_lines[i][5]),float(split_lines[i][6]))
		time_series_all.append(time.mktime(dt.timetuple()))
		lumin_all.append(float(split_lines[i][6]))
		i += 1
		try:
			char = split_lines[i][0][0]
		except: pass
	return lumi_id_to_gps_times,lumi_id_to_lumin,time_series_all,lumin_all
lumi_id_to_gps_times,lumi_id_to_lumin,time_series_all,lumin_all = read_lumi_by_ls(lumibyls_file)


ordered_triggers = ["HLT_Jet30","HLT_Jet60","HLT_Jet80","HLT_Jet110","HLT_Jet150","HLT_Jet190","HLT_Jet240","HLT_Jet300","HLT_Jet370"]
trigger_vector_dict = {}

all_lumis_A = []
all_lumis_A_times = []
for lumi_id in lumi_id_to_lumin.keys():
		if lumi_id[0] in runA_runs:
			all_lumis_A_times.append(lumi_id_to_gps_times[lumi_id])
      all_lumis_A.append(lumi_id)
      
      # need to time order
 all_lumis_A_times_sorted,all_lumis_A_sorted = (list(t) for t in zip(*sorted(zip(all_lumis_A_times,all_lumis_A))))

# replicate each vector for each trigger as a line of 0s
for trigger in ordered_triggers:
  trigger_vector_dict[trigger] = np.zeros(len(all_lumis_A_sorted))

# go thorugh the lumiblocks for each trigger, then index change to 1 if present
