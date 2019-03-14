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
total_cross_sections = [48444950000.000,36745720000.000,815912800.0,53122370.0,6359119.0,784265.0,115134.00,24262.8,1168.49,70.2242,
		       15.5537,1.84369,0.332105,0.0108721,0.000357463]

output_table = sys.argv[1]
event_file_dir = sys.argv[2]




"""
all_dirs = ["/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/MOD/12Oct2013-v1/10000/",
	   "/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/MOD/12Oct2013-v1/20000_a/",
	   "/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/MOD/12Oct2013-v1/20000_b/",
	   "/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/MOD/12Oct2013-v1/20000_c/",
	   "/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/MOD/12Oct2013-v1/20001/"]
"""

pt_codes = ["0to5","5to15","15to30","30to50","50to80","80to120","120to170","170to300","300to470","470to600","600to800","800to1000",
	    "1000to1400","1400to1800","1800"]


# key = trigger names
master_datasets_pv_events = {}
master_datasets_pvf_events = {}


for pt_code in pt_codes:
	master_datasets_pv_events[pt_code] = 0
	master_datasets_pvf_events[pt_code] = 0



for pt_code in pt_codes:
	l = 0
	print pt_code
	with open(event_file_dir+"/"+pt_code+"_by_event.txt","r") as file:
		for line in file:
			l += 1
			if l % 500000 == 0:
				print l
			#if l == 100000: break
			if "EventNum" not in line.split():
				event_num = line.split()[0]
				run_num = line.split()[1]
				lumi_num = line.split()[2]
				triggers_present = [x[:-3] for x in line.split()[3].split(",")[:-1]]
				trigger_prescales = [float(x) for x in line.split()[4].split(",")[:-1]]
				try:
					triggers_fired = [x[:-3] for x in line.split()[5].split(",")]
				except IndexError:
					triggers_fired = []
				master_datasets_pv_events[pt_code] += 1
				if len(triggers_fired) > 1:
					master_datasets_pvf_events[pt_code] += 1
					
real_total_events =0
real_fired_events =0
for pt_code in pt_codes:
	real_total_events += master_datasets_pv_events[pt_code]
	real_fired_events += master_datasets_pvf_events[pt_code]
print "here"
print output_table
with open(output_table,"w") as output:
	output.write("\\begin{table*}[h!]\n")
	output.write("\\begin{center}\n")
	output.write("\\begin{tabular}{ r @{$\quad$} r @{$\quad$} r @{$\quad$} r @{$\quad$} r @{$\quad$} r @{$\quad$}  r @{$\quad$} }\n")
	output.write("\smallest\n")
	output.write("\hline\n")
	output.write("\hline\n")
	output.write("Dataset & Events Used & Fired Events Used & Eff. Cross Sec & Total Events & Total Files & Total disc space (TB) \\\ \n")
	output.write("\hline\n")
	output.write("\hline\n")
	#output.write("trigger_name,pv_events,pvf_events,eff_lumin,eff_cross_sec,\n")
	for i, pt_code in enumerate(pt_codes):
		line = "\\texttt{"+pt_codes[i]+"}"+" & "+"{:,}".format(master_datasets_pv_events[pt_code])+" & "+"{:,}".format(master_datasets_pvf_events[pt_code])+" & "+("%.5f" %  total_cross_sections[i])+" & "+"{:,}".format(total_events[i])+" & "+"{:,}".format(total_files[i])+" & "+"{:,}".format(total_disc_space[i])+" \\\ "+"\n"
		output.write(line)
	output.write("\hline\n")
	line = "Total" + " & " + "{:,}".format(real_total_events) + " & " + "{:,}".format(real_fired_events) + " & " +"N/A" + " & " + "{:,}".format(sum(total_events)) + " & " +"{:,}".format(sum(total_files)) + " & " +str(sum(total_disc_space)) + " & " +" \\\ " + "\n"
	output.write(line)
	output.write("\hline\n")
	output.write("\hline\n")
	output.write("\end{tabular}\n")
	output.write("\caption{} \n")
	output.write("\label{table:qcd_datasets_cross_section_info}\n")
	output.write("\end{center}\n")
	output.write("\end{table*}\n")
