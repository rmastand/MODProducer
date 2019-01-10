import numpy as np
import sys
import matplotlib.pyplot as plt

input_file = sys.argv[1]

trigger_dict = {}
i = 0
with open(input_file, "r") as input:
  for line in input:
    i += 1
    if "#" in line.split():
      trigger = line.split()[1]
      trigger_dict[trigger] = (0,0) #eff lumi, times fired
      i = 0
    elif i == 1: # lumi ids
      pass
    elif i == 2: # eff lumis
      eff_lumis = line.split(",")[:-1]
      eff_lumis = [float(x) for x in eff_lumis]
      trigger_dict[trigger][0] = eff_lumis
    elif i == 3: # # times fired
      times_fired = line.split(",")[:-1]
      times_fired = [int(x) for x in times_fired]
      trigger_dict[trigger][1] = times_fired
    
for trigger in trigger_dict.keys():
  plt.figure()
  plt.scatter(trigger_dict[trigger][0],trigger_dict[trigger][0],s=1)
  plt.xlabel("Effective Luminosity")
  plt.ylabel("Times Fired")
  plt.show()
