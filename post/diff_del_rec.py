"""
parses o.txt to a ready-to-plot array of numbers
"""
# -*- coding: utf-8 -*-
import numpy as np
import sys
import datetime
import time
import csv
import matplotlib.pyplot as plt

missing_lumi_file = sys.argv[1]
lumibyls_file = sys.argv[2]
run_alumi_file = sys.argv[3]

def percent_diff(x,y):
	return np.abs(2*(x-y)/(x+y))

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


runA_ids = []

for lumi_id in lumi_id_to_lumin.keys():
		if lumi_id[0] in runA_runs:
      			runA_ids.append(lumi_id[0]+":"+lumi_id[1])
			
"""
percent diffs for runA
"""
runA_pdiffs = []
for id in runA_ids:
	runA_pdiffs.append(percent_diff(lumi_id_to_lumin[lumi_id][0],lumi_id_to_lumin[lumi_id][1]))
	

print np.mean(runA_pdiffs)
plt.figure()
plt.hist(runA_pdiffs)
plt.show()

"""
percent diffs for missing blocks
"""
missing_pdiffs = []
j = 0
with open(missing_lumi_file,"r") as missing_lumis:
	for line in missing_lumis:
		j += 1
		if j != 1:
			
			missing_pdiffs.append(percent_diff(float(line.split()[2]),float(line.split()[3])))
print np.mean(missing_pdiffs)
plt.figure()
plt.hist(missing_pdiffs)
plt.show()

