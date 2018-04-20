import numpy as np
import sys

stats_file = sys.argv[1]

with open(stats_file) as f:
    content = f.readlines()
# you may also want to remove whitespace characters like `\n` at the end of each line
content = [x.strip().split(" ") for x in content] 

by_file = {}
by_lumi = {}
for event in content:
	by_file[event[3]] = {}
	by_file[event[3]]["lumis present"] = []
	by_file[event[3]]["triggers"] = {}
	by_file[event[3]]["good_events"] = 0
	for trigger in range(4,len(event),6):
		by_file[event[3]]["triggers"][event[trigger]]={"present":0,"fired":0,"prescale1":[],"prescale2":[]}

	by_lumi[(event[0],event[2])] = {}
	by_lumi[(event[0],event[2])]["files present"] = []
	by_lumi[(event[0],event[2])]["triggers"] = {}
	by_lumi[(event[0],event[2])]["good_events"] = 0
	for trigger in range(4,len(event),6):
		by_lumi[(event[0],event[2])]["triggers"][event[trigger]]={"present":0,"fired":0,"prescale1":[],"prescale2":[]}

for event in content:
	by_file[event[3]]["good_events"] += 1
	if (event[0],event[2]) not in by_file[event[3]]["lumis present"]:
		by_file[event[3]]["lumis present"].append((event[0],event[2]))
	for trigger in range(4,len(event),6):
		by_file[event[3]]["triggers"][event[trigger]]["present"] +=1
		if [event[trigger+3]]=="true":
			by_file[event[3]]["triggers"][event[trigger]]["fired"] +=1
		by_file[event[3]]["triggers"][event[trigger]]["prescale1"].append(float(event[trigger+2]))
		by_file[event[3]]["triggers"][event[trigger]]["prescale2"].append(float(event[trigger+3]))		

	by_lumi[(event[0],event[2])]["good_events"] += 1
	if event[3] not in by_lumi[(event[0],event[2])]["files present"]:
		by_lumi[(event[0],event[2])]["files present"].append(event[3])
	for trigger in range(4,len(event),6):
		by_lumi[(event[0],event[2])]["triggers"][event[trigger]]["present"] +=1
		if [event[trigger+3]]=="true":
			by_lumi[(event[0],event[2])]["triggers"][event[trigger]]["fired"] +=1
		by_lumi[(event[0],event[2])]["triggers"][event[trigger]]["prescale1"].append(float(event[trigger+2]))
		by_lumi[(event[0],event[2])]["triggers"][event[trigger]]["prescale2"].append(float(event[trigger+3]))		

	

w = open("reg_by_file.txt","w")
w.write("filename    good events    lumi blocks present    triggers(present,fired,avg prescale val)\n")
for filename in by_file.keys():
	line = filename + "    "
	line += str(by_file[filename]["good_events"])+"    "
	for lumi in by_file[filename]["lumis present"]:
		line += str(lumi)+","
	line += "    "
	for trigger in by_file[filename]["triggers"].keys():
		line += "("+trigger+","+str(by_file[filename]["triggers"][trigger]["present"])+","
		line += str(np.mean(by_file[filename]["triggers"][trigger]["prescale1"]))+","
		line += str(np.mean(by_file[filename]["triggers"][trigger]["prescale2"]))+","
		line += str(by_file[filename]["triggers"][trigger]["fired"])+"),"
	line += "\n"
	w.write(line)

x = open("reg_by_lumi.txt","w")
x.write("lumi block    good events    files present    triggers(present,fired,avg prescale val)\n")
for lumi in by_lumi.keys():
	line = str(lumi)+"    "
	line += str(by_lumi[lumi]["good_events"])+"    "
	for filename in by_lumi[lumi]["files present"]:
		line += str(filename)+","
	line += "    "
	for trigger in by_lumi[lumi]["triggers"].keys():
		line += "("+trigger+","+str(by_lumi[lumi]["triggers"][trigger]["present"])+","
		line += str(np.mean(by_lumi[lumi]["triggers"][trigger]["prescale1"]))+","
		line += str(np.mean(by_lumi[lumi]["triggers"][trigger]["prescale2"]))+","
		line += str(by_lumi[lumi]["triggers"][trigger]["fired"])+"),"
	line += "\n"
	x.write(line)
