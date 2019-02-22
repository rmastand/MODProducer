import numpy as np
import sys
import matplotlib.pyplot as plt
import datetime

lumibyls_file = sys.argv[1]
eff_lumi_time = sys.argv[2]
fig_save = sys.argv[3]

plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 16
plt.rcParams['font.weight'] = "bold"
plt.rcParams['axes.labelsize'] = 24
plt.rcParams['xtick.labelsize'] = 18
plt.rcParams['ytick.labelsize'] = 18
plt.rcParams['legend.fontsize'] = 24
plt.rcParams['legend.fontsize'] = 24
plt.rcParams['legend.fontsize'] = 24
plt.rcParams['axes.linewidth'] = 2


plt.rcParams['xtick.major.size'] = 10
plt.rcParams['xtick.major.width'] = 2
plt.rcParams['xtick.minor.size'] = 5
plt.rcParams['xtick.minor.width'] = 2
plt.rcParams['ytick.major.size'] = 10
plt.rcParams['ytick.major.width'] = 2
plt.rcParams['ytick.minor.size'] = 5
plt.rcParams['ytick.minor.width'] = 2

plt.rc('mathtext', rm='serif')
plt.rcParams['figure.facecolor'] = "white"

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
	lumi_id_to_date = {}
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
		dt = datetime.datetime(mdy[2], mdy[0], mdy[1], hms[0], hms[1],hms[2])
		lumi_id_to_date[(run,lumi)] = str(mdy[1])+"/"+str(mdy[0])+"/"+str(mdy[2])
		i += 1
		try:
			char = split_lines[i][0][0]
		except: pass
	return lumi_id_to_lumin,lumi_id_to_date

lumi_id_to_lumin,lumi_id_to_date = read_lumi_by_ls(lumibyls_file)

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
        runA_lumin_del.append(lumi_id_to_lumin[(lumi_id.split(":")[0],lumi_id.split(":")[1])][0])
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
plt.ylabel("Luminosity (ub^-1)")
plt.xlabel("Date")
ax = plt.gca()
length = len(runA_times)-1
indices_for_xaxis = np.linspace(length/20,length,5)
indices_for_xaxis = [int(x) for x in indices_for_xaxis]
plt.xticks(np.take(runA_times,indices_for_xaxis))
labels = [item.get_text() for item in ax.get_xticklabels()]
for i,index in enumerate(indices_for_xaxis):
	labels[i] = lumi_id_to_date[(str(int(runA_lumis[index].split(":")[0])),str(int(runA_lumis[index].split(":")[1])))]	
ax.set_xticklabels(labels)
plt.savefig(fig_save)
      
      
      
