import numpy as np
import sys
import os

# make sure jet has pt > 375, eta < 1.9

all_pfcs = {}
all_pfcs_1Gev = {}

output_file = sys.argv[1]

jet_is_good = False

all_dirs = ["/Volumes/Seagate Backup Plus Drive/MODAnalyzerResults/ALL_FILES_2011_redone/10000/",
	   "/Volumes/Seagate Backup Plus Drive/MODAnalyzerResults/ALL_FILES_2011_redone/20000_a/",
	   "/Volumes/Seagate Backup Plus Drive/MODAnalyzerResults/ALL_FILES_2011_redone/20000_b/",
	   "/Volumes/Seagate Backup Plus Drive/MODAnalyzerResults/ALL_FILES_2011_redone/20000_c/",
	   "/Volumes/Seagate Backup Plus Drive/MODAnalyzerResults/ALL_FILES_2011_redone/20001/"]

l = 0
for dat_dir in all_dirs:
	for dat_file in os.listdir(dat_dir):
		if "particles" in dat_file:
		    with open(dat_dir+"/"+dat_file, "r") as file:
		      l += 1
		      print l, 1223
		      for line in file:
			if ("BeginJetProperties" in line.split()) and ("#" not in line.split()):
			  jet_pt = float(line.split()[2])
			  jet_eta = float(line.split()[4])
			  if (jet_pt > 375) and (-1.9 < jet_eta < 1.9):
			    jet_is_good = True
			  else: jet_is_good = False

			if ("BeginParticle" in line.split()) and ("#" not in line.split()):
			  if jet_is_good:
				  particle_pt = float(line.split()[1])
				  particle_id = int(line.split()[3])
				  try: all_pfcs[particle_id] += 1
				  except KeyError: all_pfcs[particle_id] = 1
				  if particle_pt > 1:
				    try: all_pfcs_1Gev[particle_id] += 1
				    except KeyError: all_pfcs_1Gev[particle_id] = 1


pdg_id_order = [11, -11, 13, -13, 211, -211]
pdg_id_order_names = ["Electron (e$^-$)", "Positron (e$^+$)", "Muon ($\mu^-$)", "Antimuon ($\mu^+$)", "Positive Hadron ($\pi^+$)", "Negative Hadron ($\pi^-$)"]
pdg_id_order_2 = [22, 130]
pdg_id_order_2_names = ["Photon ($\gamma$)", "Neutral Hadron ($K^0_L$)"]
print all_pfcs
print all_pfcs_1Gev
with open(output_file,"w") as output:
  output.write("\\begin{table}[h!]\n")
  output.write("\\begin{center}\n")
  output.write("\\begin{tabular}{ r@{$\quad$} l @{$\quad$} r @{$\quad$} r }\n")
  output.write("\hline\n")
  output.write("\hline\n")
  output.write("Code & Candidate & Total Count & $\pt > $ 1GeV \\\ \n")
  output.write("\hline\n")
  output.write("\hline\n")
  for i, object in enumerate(pdg_id_order):
    output.write(str(object)+ " & "+str(pdg_id_order_names[i])+" & " "{:,}".format(all_pfcs[object])+" & " "{:,}".format(all_pfcs_1Gev[object]) +"\\\ \n")
  output.write("\hline\n")
  for i, object in enumerate(pdg_id_order_2):
	try: output.write(str(object)+ " & "+str(pdg_id_order_2_names[i])+" & " +"{:,}".format(all_pfcs[object])+" & " "{:,}".format(all_pfcs_1Gev[object]) +"\\\ \n")
  	except KeyError: output.write(str(object)+ " & "+str(pdg_id_order_2_names[i])+" & " +"{:,}".format(all_pfcs[object])+" & " +str(0) +"\\\ \n")

  output.write("\hline\n")
  output.write("\hline\n")
  output.write("\end{tabular} \n")
  output.write("\end{tabular} \n")
  output.write("\caption{} \n")
  output.write("\label{table:object_count} \n")
  output.write("\end{table}\n")

