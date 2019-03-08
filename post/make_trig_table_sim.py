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

total_files = [55, 83, 5519, 277, 299, 317, 334, 387, 382, 274, 271, 295, 131, 182, 75]
total_events = [1000025, 1495884, 9978850, 5837856, 5766430, 5867864, 5963264, 5975592, 5975016, 3967154, 3988701, 3945269,
	       1956893, 1991792, 996500]
total_disc_space = [.1378, .2233, 1.7, 1.0, 1.1, 1.2, 1.2, 1.3, 1.4, .9571, .9768, .9743, .4841, .4914, .2434]
files_used = [55, 83, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 131, 182, 75]


output_table = sys.argv[1]
event_file = sys.argv[2]




"""
all_dirs = ["/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/MOD/12Oct2013-v1/10000/",
	   "/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/MOD/12Oct2013-v1/20000_a/",
	   "/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/MOD/12Oct2013-v1/20000_b/",
	   "/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/MOD/12Oct2013-v1/20000_c/",
	   "/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/MOD/12Oct2013-v1/20001/"]
"""

pt_codes = ["0-5","5-15","15-30","30-50","50-80","80-120","120-170","170-300","300-470","470-600","600-800","800-1000",
	    "1000-1400","1400-1800","1800"]


# key = trigger names
master_triggers_pv_lumis = {}
master_triggers_pv_events = {}
master_triggers_pvf_events = {}
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

l = 0
with open(event_file,"r") as file:
	for line in file:
		l += 1
		if l % 500000 == 0:
			print l
		#if l == 500000: break
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
	output.write("\\begin{table*}[h!]\n")
	output.write("\\begin{center}\n")
	output.write("\\begin{tabular}{ r @{$\quad$} r @{$\quad$} r @{$\quad$} r @{$\quad$} r @{$\quad$} r @{$\quad$}  r @{$\quad$} }\n")
	output.write("\smallest\n")
	output.write("\hline\n")
	output.write("\hline\n")
	output.write("Trigger Name & Events Used & Fired Events Used & Eff. Cross Sec & Total Events & Total Files & Total disc space\\\ \n")
	output.write("\hline\n")
	output.write("\hline\n")
	#output.write("trigger_name,pv_events,pvf_events,eff_lumin,eff_cross_sec,\n")
	for trigger in single_jet:
		line = "\\texttt{"+trigger.replace("_","\_")+"}"+" & "+"{:,}".format(len(master_triggers_pv_lumis[trigger].keys()))+" & "+"{:,}".format(master_triggers_pvf_events[trigger])+" & "+("%.2f" %  master_triggers_eff_lumi[trigger])+" & "+("%.6f" % (float(master_triggers_pvf_events[trigger])/float(master_triggers_eff_lumi[trigger])))+" \\\ "+"\n"
		output.write(line)
	output.write("\hline\n")
	for trigger in di_jet:
		line = "\\texttt{"+trigger.replace("_","\_")+"}"+" & "+"{:,}".format(len(master_triggers_pv_lumis[trigger].keys()))+" & "+"{:,}".format(master_triggers_pvf_events[trigger])+" & "+("%.2f" %  master_triggers_eff_lumi[trigger])+" & "+("%.6f" % (float(master_triggers_pvf_events[trigger])/float(master_triggers_eff_lumi[trigger])))+" \\\ "+"\n"
		output.write(line)
	output.write("\hline\n")
	for trigger in diu_jet:
		line = "\\texttt{"+trigger.replace("_","\_")+"}"+" & "+"{:,}".format(len(master_triggers_pv_lumis[trigger].keys()))+" & "+"{:,}".format(master_triggers_pvf_events[trigger])+" & "+("%.2f" %  master_triggers_eff_lumi[trigger])+" & "+("%.6f" % (float(master_triggers_pvf_events[trigger])/float(master_triggers_eff_lumi[trigger])))+" \\\ "+"\n"
		output.write(line)
	output.write("\hline\n")
	for trigger in misc:
		line = "\\texttt{"+trigger.replace("_","\_")+"}"+" & "+"{:,}".format(len(master_triggers_pv_lumis[trigger].keys()))+" & "+"{:,}".format(master_triggers_pvf_events[trigger])+" & "+("%.2f" %  master_triggers_eff_lumi[trigger])+" & "+("%.6f" % (float(master_triggers_pvf_events[trigger])/float(master_triggers_eff_lumi[trigger])))+" \\\ "+"\n"
		output.write(line)
	output.write("\hline\n")
	line = "Total" + " & " + "{:,}".format(len(runA_blocks)) + " & " + "{:,}".format(total_pv_events) + " & " + "{:,}".format(total_pvf_events) + " & "+("%.2f" % total_eff_lumi)+" & "+"N/A"+ " \\\ " + "\n"
	output.write(line)
	output.write("\hline\n")
	output.write("\hline\n")
	output.write("\end{tabular}\n")
	output.write("\caption{} \n")
	output.write("\label{table:full list of triggers}\n")
	output.write("\end{center}\n")
	output.write("\end{table}\n")
