import numpy as np
import sys

# make sure jet has pt > 85, eta < 1.9

all_pfcs = {}
all_pfcs_1Gev = {}

dat_file = sys.argv[1]

jet_is_good = false

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
        
    
