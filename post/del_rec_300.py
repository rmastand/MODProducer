import numpy as np
import sys
import matplotlib.pyplot as plt

lumibyls_file = sys.argv[1]
eff_lumi_time = sys.argv[2]

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
	id_to_time = {}
	time_to_id = {}
	time_to_lumin = {}
	lumi_id_to_lumin = {}
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

"""
line 1 = runA ids
line 2 = runA times
line 3 = runA rec lumi
line 6 = 300 times
line 7 = 300 rec lumi
"""

runA_times = []
runA_lumin_del = []
runA_lumin_rec = []
jet300_times = []
jet300_lumin_rec = []
runA_lumis = []

l = 0
with open(eff_lumi_time,"r") as file:
  for line in file:
    l += 1
    if l == 1:
      runA_lumis = line.split(",")[:-1]
      for lumi_id in runA_lumis:
        runA_lumin_del.append(lumi_id_to_lumin[(lumi_id.split(":")[0],lumi_id.split(":")[1])])
    elif l == 2:
      runA_times = [float(x) for x in line.split(",")[:-1]]
    elif l == 3:
      runA_lumin_rec = [float(x) for x in line.split(",")[:-1]]
    elif l == 6:
      jet300_times = [float(x) for x in line.split(",")[:-1]]
    elif l == 7:
      jet300_lumin_rec = [float(x) for x in line.split(",")[:-1]]

plt.figure()
plt.plot(runA_times,np.cumsum(runA_lumin_del),label="RunA Delivered")
plt.plot(runA_times,np.cumsum(runA_lumin_rec),label="RunA Recorded")
plt.plot(jet300_times,np.cumsum(jet300_lumin_rec),label="Jet300 Recorded")
plt.legend()
plt.show()
      
      
      
