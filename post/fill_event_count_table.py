import numpy as np
import sys
import os

# make sure jet has pt > 85, eta < 1.9

all_pfcs = {}
all_pfcs_1Gev = {}

output_file = sys.argv[1]

jet_is_good = False

all_dirs = ["/Volumes/Seagate Backup Plus Drive/MODAnalyzerResults/2011_pfc_dat_files/10000/",
	   "/Volumes/Seagate Backup Plus Drive/MODAnalyzerResults/2011_pfc_dat_files/20000_a/",
	   "/Volumes/Seagate Backup Plus Drive/MODAnalyzerResults/2011_pfc_dat_files/20000_b/",
	   "/Volumes/Seagate Backup Plus Drive/MODAnalyzerResults/2011_pfc_dat_files/20000_c/",
	   "/Volumes/Seagate Backup Plus Drive/MODAnalyzerResults/2011_pfc_dat_files/20001/"]
all_dirs = ["/Volumes/Seagate Backup Plus Drive/MODAnalyzerResults/2011_pfc_dat_files/20000_a/"]

l = 0
for dat_dir in all_dirs:
	for dat_file in os.listdir(dat_dir):
    with open(dat_dir+"/"+dat_file, "r") as file:
      l += 1
      print l, 1223
      for line in file:
        if ("BeginJetProperties" in line.split()) and ("#" not in line.split()):
          jet_pt = float(line.split()[2])
          jet_eta = float(line.split()[4])
          if (jet_pt > 85) and (-1.9 < jet_eta < 1.9):
            jet_is_good = True
          else: jet_is_good = False

        if ("BeginParticle" in line.split()) and ("#" not in line.split()):
          particle_pt = float(line.split()[1])
          particle_id = int(line.split()[3])
          try: all_pfcs[particle_id] += 1
          except KeyError: all_pfcs[particle_id] = 1
          if particle_pt > 1:
            try: all_pfcs_1Gev[particle_id] += 1
            except KeyError: all_pfcs_1Gev[particle_id] = 1
          

pdg_id_order = [11, -11, 13, -13, 211, -211]
pdg_id_order_names = ["Electron", "Positron", "Muon", "Antimuon", "Positive Hadron", "Negative Hadron"]
pdg_id_order_2 = [22, 130, 1, 2]
pdg_id_order_2_names = ["Photon", "Neutral Hadron", "Object", "Object"]
  
with open(output_file,"w") as output:
  output.write("\\begin{table}[h!]\n")
  output.write("\\begin{center}\n")
  output.write("\\begin{tabular}{ |r|c|c|r| }\n")
  output.write("\hline\n")
  output.write("\hline\n")
  output.write("Code & Candidate & Total Count & $\pt > $ 1GeV \\\ \n")
  output.write("\hline\n")
  output.write("\hline\n")
  for i, object in enumerate(pdg_id_order):
    output.write(str(object)+ " & "+str(pdg_id_order_names[i])+" & " +str(all_pfcs[object])+" & " +str(all_pfcs_1Gev[object])+" & " +"\\\ \n")
  output.write("\hline\n")
  for i, object in enumerate(pdg_id_order_2):
    output.write(str(object)+ " & "+str(pdg_id_order_2_names[i])+" & " +str(all_pfcs[object])+" & " +str(all_pfcs_1Gev[object])+" & " +"\\\ \n")
  output.write("\hline\n")
  output.write("\hline\n")
  output.write("\end{tabular} \n")
  output.write("\end{center}\n")
  output.write("\end{table}\n")

