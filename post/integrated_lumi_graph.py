import numpy as np
import pandas as pd
import datetime
import time
import sys
import ast
import matplotlib.pyplot as plt


lumibyls_file = sys.argv[1]
lumibyls = open(lumibyls_file)
lines =  lumibyls.readlines()
split_lines = [line.split(",") for line in lines][2:]
char = ""
lumibyls_gps_times = {}
lumibyls_delivered= []
lumibyls_recorded = []
lumibyls_time = []
i = 0
choose_xticks = np.ceil(np.linspace(1,len(split_lines),6))
x_ticks = []
x_tick_labels = []
while char !="#":
	run = split_lines[i][0].split(":")[0]
	lumi = split_lines[i][1].split(":")[0]
	date = split_lines[i][2].split(" ")[0]
	tim = split_lines[i][2].split(" ")[1]
	mdy = [int(x) for x in date.split("/")]
	hms = [int(x) for x in tim.split(":")]
	dt = datetime.datetime(mdy[2], mdy[0], mdy[1], hms[0], hms[1],hms[2])
	gpstime = time.mktime(dt.timetuple())
	lumibyls_gps_times[(run,lumi)] = gpstime
	lumibyls_delivered.append(float(split_lines[i][5]))
	lumibyls_recorded.append(float(split_lines[i][6]))
	lumibyls_time.append(gpstime)
	if i in choose_xticks:
		x_ticks.append(gpstime)
		x_tick_labels.append(str(mdy[0])+"/"+str(mdy[1]))
	i += 1
        char = split_lines[i][0][0]



runalumi_file = sys.argv[2]
runalumi_data = open(runalumi_file)
lines =  runalumi_data.readlines()
split_lines = [line.split("|") for line in lines][4:]
char = ""
rlumi_gps_times = {}
rlumi_delivered= []
rlumi_recorded = []
rlumi_time = []
i = 0

while char !="+":
	run = split_lines[i][0].strip().split(":")[0]
	lumi = split_lines[i][1].strip().split(":")[0]
	date = split_lines[i][2].strip().split(" ")[0]
	tim = split_lines[i][2].strip().split(" ")[1]
	mdy = [int(x) for x in date.strip().split("/")]
	hms = [int(x) for x in tim.strip().split(":")]
	dt = datetime.datetime(mdy[2], mdy[0], mdy[1], hms[0], hms[1],hms[2])
	rgpstime = time.mktime(dt.timetuple())
	rlumi_gps_times[(run,lumi)] = rgpstime
	rlumi_delivered.append(float(split_lines[i][5]))
	rlumi_recorded.append(float(split_lines[i][6]))
	rlumi_time.append(rgpstime)

	i += 1
	try:
		char = split_lines[i][0][0]
	except: pass




plt.figure()
times,lumi_rec = (list(t) for t in zip(*sorted(zip(lumibyls_time,lumibyls_recorded))))
times,lumi_del = (list(t) for t in zip(*sorted(zip(lumibyls_time,lumibyls_delivered))))

plt.plot(times,np.cumsum(lumi_del),label = "delivered")
plt.plot(times,np.cumsum(lumi_rec),label="recorded")
times,rlumi_rec = (list(t) for t in zip(*sorted(zip(rlumi_time,rlumi_recorded))))
times,rlumi_del = (list(t) for t in zip(*sorted(zip(rlumi_time,rlumi_delivered))))
plt.plot(times,np.cumsum(rlumi_del),label = "rdelivered")
plt.plot(times,np.cumsum(rlumi_rec),label="rrecorded")
plt.xlabel("GPS time (month/day)")
ax = plt.gca()
ax.set(xticks=x_ticks, xticklabels=x_tick_labels)
plt.legend(loc = "upper left")
plt.ylabel("integrated luminosity (/ub)")
plt.show()
plt.savefig("integrated_lumi.png")
