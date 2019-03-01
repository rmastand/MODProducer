import numpy as np
import sys

# make sure jet has pt > 85, eta < 1.9

all_pfcs = {}
all_pfcs_1Gev = {}

dat_file = sys.argv[1]
output_file = sys.argv[2]

jet_is_good = False

with open(dat_file, "r") as file:
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
          
print all_pfcs
print
print all_pfcs_1Gev
   
pdg_id_order = [11, -11, 13, -13, 211, -211]
pdg_id_order_names = ["Electron", "Positron", "Muon", "Antimuon", "Positive Hadron", "Negative Hadron"]
pdg_id_order_2 = [22, 130, 1, 2]
pdg_id_order_2_names = ["Photon", "Neutral Hadron", "Object", "Object"]
  
with open(output_file,"w") as output:
  output.write("\begin{table}[h!]\n")
  output.write("\begin{center}\n")
  output.write("\begin{tabular}{ |r|c|c|r| }\n")
  output.write("\hline\n")
  output.write("\hline\n")
  output.write("Code & Candidate & Total Count & $\pt > $ 1GeV \\\ \n")
  output.write("\hline\n")
  output.write("\hline\n")
  for i, object in enumerate(pdg_id_order):
    output.write(object+ " & "+pdg_id_order_names[i]  " & " +all_pfcs[object]+" & " +all_pfcs_1Gev[object]+" & " +"\\\ \n")
  output.write("\hline\n")
  for i, object in enumerate(pdg_id_order_2):
    output.write(object+ " & "+pdg_id_order_2_names[i]  " & " +all_pfcs[object]+" & " +all_pfcs_1Gev[object]+" & " +"\\\ \n")
  output.write("\hline\n")
  output.write("\hline\n")
  output.write("\end{tabular} \n")
  output.write("\end{center}\n")
  output.write("\end{table}\n")

