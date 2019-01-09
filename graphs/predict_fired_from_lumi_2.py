# -*- coding: utf-8 -*-
import numpy as np
import sys

parsed_by_event = sys.argv[1]
lumibyls_file = sys.argv[2]

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
		lumi_id_to_lumin[(run,lumi)] = (float(split_lines[i][5]),float(split_lines[i][6]))
		i += 1
		try:
			char = split_lines[i][0][0]
		except: pass
	return lumi_id_to_lumin



lumi_id_to_lumin = read_lumi_by_ls(lumibyls_file)
i = 0
rev_ordered_triggers = ["HLT_Jet30","HLT_Jet60","HLT_Jet80","HLT_Jet110","HLT_Jet150","HLT_Jet190","HLT_Jet240","HLT_Jet300","HLT_Jet370"][::-1]


# structure: {trigger:{lumiblock:(prescale,times_fired)}}
master_dict = {}
for trigger in rev_ordered_triggers:
  master_dict[trigger] = {}

with open(parsed_by_event,"r") as event_listing:
  for line in event_listing:
    if i < 100:
      i += 1
      if i % 10000 == 0:
        print "on line "+ str(i)
      if "EventNum" not in line.split(): #just ignores the top line
        lumi_id = (line.split()[1],line.split()[2])
        triggers_present = line.split()[3].split(",")
        # cuts the version numbers out
        triggers_present = [x[:-3] for x in triggers_present]
        triggers_fired = line.split()[5].split(",")
        triggers_fired = [x[:-3] for x in triggers_fired]
        prescales = line.split()[4].split(",")[-1]
        prescales = [float(x) for x in prescales]

        for j, present_trigger in enumerate(triggers_present):
          if present_trigger in rev_ordered_triggers:
            if lumi_id not in master_dict[trigger].keys():
              master_dict[trigger][lumi_id] = {"prescale":0,"times_fired":0}
	    try:
            	master_dict[trigger][lumi_id]["prescale"] = prescales[j]
	    except IndexError:
		print prescales
		print triggers_present
		print present_trigger
            if present_trigger in triggers_fired:   
              master_dict[trigger][lumi_id]["times_fired"] += 1 
    else: print master_dict
      
      
