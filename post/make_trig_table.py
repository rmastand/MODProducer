import numpy as np
import datetime
import time
import sys
import ast
import os
import csv
import matplotlib.pyplot as plt

"""
USED FOR THE PAPER
ALL INFORMATION IS FOR VALID LUMIS
columns: trigger name, present events, fired events
makes use of parse_by_event output
columns
eventnum runnum luminum triggerspresent triggerprescales triggersfired
"""

# setting the ordering
all_triggers = ["HLT_Jet30","HLT_Jet60","HLT_Jet80","HLT_Jet110","HLT_Jet150","HLT_Jet190","HLT_Jet240","HLT_Jet300",
		"HLT_Jet370","HLT_Jet800","HLT_DiJetAve30",
		"HLT_DiJetAve60","HLT_DiJetAve80","HLT_DiJetAve110","HLT_DiJetAve150","HLT_DiJetAve190",
		"HLT_DiJetAve240","HLT_DiJetAve300","HLT_DiJetAve370","HLT_DiJetAve15U","HLT_DiJetAve30U","HLT_DiJetAve50U",
		"HLT_DiJetAve70U","HLT_DiJetAve100U",
		"HLT_DiJetAve140U","HLT_DiJetAve180U","HLT_DiJetAve300U",
		"HLT_Jet240_CentralJet30_BTagIP","HLT_Jet270_CentralJet30_BTagIP","HLT_Jet370_NoJetID"]

single_jet = ["HLT_Jet30","HLT_Jet60","HLT_Jet80","HLT_Jet110","HLT_Jet150","HLT_Jet190","HLT_Jet240","HLT_Jet300",
		"HLT_Jet370","HLT_Jet800"]
di_jet = ["HLT_DiJetAve30",
		"HLT_DiJetAve60","HLT_DiJetAve80","HLT_DiJetAve110","HLT_DiJetAve150","HLT_DiJetAve190",
		"HLT_DiJetAve240","HLT_DiJetAve300","HLT_DiJetAve370"]
diu_jet = ["HLT_DiJetAve15U","HLT_DiJetAve30U","HLT_DiJetAve50U",
		"HLT_DiJetAve70U","HLT_DiJetAve100U",
		"HLT_DiJetAve140U","HLT_DiJetAve180U","HLT_DiJetAve300U"]
misc = ["HLT_Jet240_CentralJet30_BTagIP","HLT_Jet270_CentralJet30_BTagIP","HLT_Jet370_NoJetID"]

lumibyls_file = sys.argv[1]
output_table = sys.argv[2]
event_file = sys.argv[3]

"""
all_dirs = ["/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/MOD/12Oct2013-v1/10000/",
	   "/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/MOD/12Oct2013-v1/20000_a/",
	   "/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/MOD/12Oct2013-v1/20000_b/",
	   "/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/MOD/12Oct2013-v1/20000_c/",
	   "/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/MOD/12Oct2013-v1/20001/"]
"""

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
lumi_id_to_gps_times,lumi_id_to_lumin = read_lumi_by_ls(lumibyls_file)


# key = trigger names
master_triggers_pv_lumis = {}
master_triggers_pv_events = {}
master_triggers_pvf_events = {}
master_triggers_pvf_lumi_count = {}
master_triggers_eff_lumi = {}
master_triggers_x_section = {}
total_pv_events = 0
total_pvf_events = 0
total_eff_lumi = 0
total_x_section = {}
total_lumis = {}

for trigger in all_triggers:
	master_triggers_pv_lumis[trigger] = {}
	master_triggers_x_section[trigger] = {}
	master_triggers_eff_lumi[trigger] = 0
	master_triggers_pvf_lumi_count[trigger] = 0

l = 0
with open(event_file,"r") as file:
	for line in file:
		l += 1
		if l % 500000 == 0:
			print l
		if l == 500000: break
		if "EventNum" not in line.split():
			event_num = line.split()[0]
			run_num = line.split()[1]
			lumi_num = line.split()[2]
			triggers_present = [x[:-3] for x in line.split()[3].split(",")[:-1]]
			trigger_prescales = [float(x) for x in line.split()[4].split(",")[:-1]]
			triggers_fired = [x[:-3] for x in line.split()[5].split(",")]
			total_pv_events += 1
			if len(triggers_fired) > 1:
				total_pvf_events += 1
			try: total_lumis[(run_num,lumi_num)] += 1
			except KeyError: 
				total_eff_lumi += lumi_id_to_lumin[(run_num,lumi_num)][1]
				total_lumis[(run_num,lumi_num)] = 0
			for i,trigger in enumerate(triggers_present):
				eff_lumi = lumi_id_to_lumin[(run_num,lumi_num)][1]/trigger_prescales[i]
				try: master_triggers_pv_events[trigger] += 1
				except KeyError: master_triggers_pv_events[trigger] = 1
				
				try: master_triggers_pv_lumis[trigger][(run_num,lumi_num)] += 1
				except KeyError: # means that the lumiblock has not already been looked at by THAT TRIGGER
					master_triggers_eff_lumi[trigger] += eff_lumi
					master_triggers_pvf_lumi_count[trigger] += 1
					master_triggers_pv_lumis[trigger][(run_num,lumi_num)] = 0
				
				
				if trigger in triggers_fired:
					try: master_triggers_pvf_events[trigger] += 1
					except KeyError: master_triggers_pvf_events[trigger] = 1
					try: master_triggers_x_section[trigger][(run_num,lumi_num)][0] += 1
					except KeyError: master_triggers_x_section[trigger][(run_num,lumi_num)] = [1,eff_lumi]
					
master_triggers_crossec_final = {}

for trigger in master_triggers_x_section.keys():
	xsec = 0
	for lumi_id in master_triggers_x_section[trigger]:
		try:
			xsec += master_triggers_x_section[trigger][lumi_id][0]/master_triggers_x_section[trigger][lumi_id][1]
		except ZeroDivisionError: xsec += 0
	master_triggers_crossec_final[trigger] = xsec/len(master_triggers_x_section[trigger])

print "here"
print output_table
with open(output_table,"w") as output:
	output.write("\\begin{table}[h!]\n")
	output.write("\\begin{center}\n")
	output.write("\\begin{tabular}{ r @{$\quad$} r @{$\quad$} r @{$\quad$} r @{$\quad$} r @{$\quad$} r @{$\quad$} }\n")
	output.write("\smallest\n")
	output.write("\hline\n")
	output.write("\hline\n")
	output.write("Trigger Name & Valid Lumis & Valid Events & Fired Events & Eff. Lumin & Eff. Cross Sec \\\ \n")
	output.write("\hline\n")
	output.write("\hline\n")
	#output.write("trigger_name,pv_events,pvf_events,eff_lumin,eff_cross_sec,\n")
	for trigger in single_jet:
		line = "\\texttt{"+trigger.replace("_","\_")+"}"+" & "+"{:,}".format(master_triggers_pv_events[trigger])+" & "+"{:,}".format(master_triggers_pvf_events[trigger])+" & "+("%.2f" %  master_triggers_eff_lumi[trigger])+" & "+("%.6f" % (float(master_triggers_pvf_events[trigger])/float(master_triggers_eff_lumi[trigger])))+" \\\ "+"\n"
		output.write(line)
	output.write("\hline\n")
	for trigger in di_jet:
		line = "\\texttt{"+trigger.replace("_","\_")+"}"+" & "+"{:,}".format(master_triggers_pv_events[trigger])+" & "+"{:,}".format(master_triggers_pvf_events[trigger])+" & "+("%.2f" %  master_triggers_eff_lumi[trigger])+" & "+("%.6f" % (float(master_triggers_pvf_events[trigger])/float(master_triggers_eff_lumi[trigger])))+" \\\ "+"\n"
		output.write(line)
	output.write("\hline\n")
	for trigger in diu_jet:
		line = "\\texttt{"+trigger.replace("_","\_")+"}"+" & "+"{:,}".format(master_triggers_pv_events[trigger])+" & "+"{:,}".format(master_triggers_pvf_events[trigger])+" & "+("%.2f" %  master_triggers_eff_lumi[trigger])+" & "+("%.6f" % (float(master_triggers_pvf_events[trigger])/float(master_triggers_eff_lumi[trigger]))+" \\\ "+"\n"
		output.write(line)
	output.write("\hline\n")
	for trigger in misc:
		line = "\\texttt{"+trigger.replace("_","\_")+"}"+" & "+"{:,}".format(master_triggers_pv_events[trigger])+" & "+"{:,}".format(master_triggers_pvf_events[trigger])+" & "+("%.2f" %  master_triggers_eff_lumi[trigger])+" & "+("%.6f" % (float(master_triggers_pvf_events[trigger])/float(master_triggers_eff_lumi[trigger])))+" \\\ "+"\n"
		output.write(line)
	output.write("\hline\n")
	line = "Total" + " & " + "{:,}".format(master_triggers_pvf_lumi_count[trigger]) + " & " + "{:,}".format(total_pv_events) + " & " + "{:,}".format(total_pvf_events) + " & "+("%.2f" % total_eff_lumi)+" & "+"N/A"+ " \\\ " + "\n"
	output.write(line)
	output.write("\hline\n")
	output.write("\hline\n")
	output.write("\end{tabular}\n")
	output.write("\caption{} \n")
	output.write("\label{table:full list of triggers}\n")
	output.write("\end{center}\n")
	output.write("\end{table}\n")
