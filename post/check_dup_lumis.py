import numpy as np
import datetime
import time
import sys
import ast
import os
import csv
import matplotlib.pyplot as plt

"""generates file trig dicts, prints them to 1 dict for each file"""

lumibyls_file = sys.argv[1]
#mod_file_inpur_dir = sys.argv[2]

all_dirs = ["/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/stats/12Oct2013-v1/10000/",
	   "/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/stats/12Oct2013-v1/20000_a/",
	   "/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/stats/12Oct2013-v1/20000_b/",
	   "/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/stats/12Oct2013-v1/20000_c/",
	   "/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/stats/12Oct2013-v1/20001/"]


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
		i += 1
		try:
			char = split_lines[i][0][0]
		except: pass
	return lumi_id_to_gps_times,lumi_id_to_lumin

def is_lumi_valid(lumi_id, lumi_id_to_lumin):
	"""
	lumi_id = (run,lumiBlock)
	"""
	try:
		luminosity = lumi_id_to_lumin[lumi_id]
		return 1
	except KeyError:
		pass

lumi_id_to_gps_times,lumi_id_to_lumin = read_lumi_by_ls(lumibyls_file)


def read_stats_file(stats_file,file_name,i,num_files):
	"""
	prints a dict of triggers FOR EACH MOD file
	keys are triggers names (with versions)
	subdicts are lists of good lumis the trigger was present for and the corresponding good prescale values
	
	each n correponds to a different trigger name
	line n = uncut trigger name (with version)
	line n+1 = list of good lumins ids trig_dict["good_lumis"]
	line n+2 = list of good prescales trig_dict["good_prescales"]
	line n+3 = list of lumi: # times fired paired. Comes from a dict where lumi id is the key and # times fired is the value trig_dict["fired"]
	"""
	valid_lumis = []
	all_lumis = []
	num_valid_events = 0
	num_total_events = 0

	with open(stats_file) as file:
		
		for line in file:
			# MOST CODE TAKEN FROM GET_TRIGGER_INFO.py
			# keeps track of the run, lumiBlock
			# this should signal each separate event
			if ("File" in line.split()) and ("#" not in line.split()):
				num_valid_events,num_total_events = int(line.split()[3]), int(line.split()[2])
			if ("Block" in line.split()) and ("#" not in line.split()):	
				run,lumiBlock = line.split()[1],line.split()[2]
				
				
				all_lumis.append(run+":"+lumiBlock)
				
				if is_lumi_valid((run,lumiBlock),lumi_id_to_lumin):
						valid_lumis.append(run+":"+lumiBlock)
	return valid_lumis,all_lumis,num_valid_events,num_total_events

		
all_valid_lumis = []
all_num_events_valid = []
all_num_events_total = []
all_num_lumis_valid = []
all_num_lumis_total = []
i = 1
num_files = 1223
for dire in all_dirs:
	for file in os.listdir(dire):
		# if file has not already been processed
		#print "Processing file " + file + ", File "+str(i)+" of " + str(num_files)
		valid_lumis,all_lumis,num_valid_events,num_total_events = read_stats_file(dire+"/"+file,file,i,num_files)
		all_valid_lumis += valid_lumis
		i += 1
		all_num_events_valid.append(num_valid_events)
		all_num_events_total.append(num_total_events)
		all_num_lumis_valid.append(len(valid_lumis))
		all_num_lumis_total.append(len(all_lumis))
print "all lumis duplicated, total lumis"
print set([x for x in all_valid_lumis if all_valid_lumis.count(x) > 1])
print len(set([x for x in all_valid_lumis if all_valid_lumis.count(x) > 1]))
print len(set(all_valid_lumis))


plt.figure()
plt.hist(all_num_events_valid,bins=50)
plt.title("Number of valid events per file")
plt.show()

plt.figure()
plt.hist(all_num_events_total,bins=50)
plt.title("Number of events per file")
plt.show()

plt.figure()
plt.hist(all_num_lumis_valid,bins=50)
plt.title("Number of valid lumiblocks per file")
plt.show()

plt.figure()
plt.hist(all_num_lumis_total,bins=50)
plt.title("Number of lumiblocks per file")
plt.show()



