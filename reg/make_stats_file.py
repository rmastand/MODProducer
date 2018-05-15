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
	if event[3] not in by_file.keys():
		by_file[event[3]] = {}
		by_file[event[3]]["lumis present"] = [(event[0],event[2])]
		by_file[event[3]]["events"] = 1
		by_file[event[3]]["triggers"]={}
		for trigger in range(4,len(event),6):
			by_file[event[3]]["triggers"][event[trigger]]={"present":1,"fired":int(event[trigger+4]=="true"),"prescale1":[float(event[trigger+2])],"prescale2":[float(event[trigger+3])]}
	else:
		if (event[0],event[2]) not in by_file[event[3]]["lumis present"]:
			by_file[event[3]]["lumis present"].append((event[0],event[2]))
		by_file[event[3]]["events"]+=1
		for trigger in range(4,len(event),6):
			if event[trigger] not in by_file[event[3]]["triggers"].keys():
				by_file[event[3]]["triggers"][event[trigger]]={"present":1,"fired":int(event[trigger+4]=="true"),"prescale1":[float(event[trigger+2])],"prescale2":[float(event[trigger+3])]}
			else:
				by_file[event[3]]["triggers"][event[trigger]]["present"]+=1
				by_file[event[3]]["triggers"][event[trigger]]["fired"]+=int(event[trigger+4]=="true")
				by_file[event[3]]["triggers"][event[trigger]]["prescale1"].append(float(event[trigger+2]))
				by_file[event[3]]["triggers"][event[trigger]]["prescale2"].append(float(event[trigger+3]))





	if (event[0],event[2]) not in by_lumi.keys():
		by_lumi[(event[0],event[2])] = {}
		by_lumi[(event[0],event[2])]["files present"] = [event[3]]
		by_lumi[(event[0],event[2])]["events"] = 1
		by_lumi[(event[0],event[2])]["triggers"]={}
		for trigger in range(4,len(event),6):
			by_lumi[(event[0],event[2])]["triggers"][event[trigger]]={"present":1,"fired":int(event[trigger+4]=="true"),"prescale1":[float(event[trigger+2])],"prescale2":[float(event[trigger+3])]}
	else:
		if event[3] not in by_lumi[(event[0],event[2])]["files present"]:
			by_lumi[(event[0],event[2])]["files present"].append(event[3])
		by_lumi[(event[0],event[2])]["events"]+=1
		for trigger in range(4,len(event),6):
			if event[trigger] not in by_lumi[(event[0],event[2])]["triggers"].keys():
				by_lumi[(event[0],event[2])]["triggers"][event[trigger]]={"present":1,"fired":int(event[trigger+4]=="true"),"prescale1":[float(event[trigger+2])],"prescale2":[float(event[trigger+3])]}
			else:
				by_lumi[(event[0],event[2])]["triggers"][event[trigger]]["present"]+=1
				by_lumi[(event[0],event[2])]["triggers"][event[trigger]]["fired"]+=int(event[trigger+4]=="true")
				by_lumi[(event[0],event[2])]["triggers"][event[trigger]]["prescale1"].append(float(event[trigger+2]))
				by_lumi[(event[0],event[2])]["triggers"][event[trigger]]["prescale2"].append(float(event[trigger+3]))


	
	

w = open("reg_by_file.txt","w")
w.write("filename    events    lumi blocks present    triggers(present,fired,avg prescale val)\n")
for filename in by_file.keys():
	line = filename + "    "
	line += str(by_file[filename]["events"])+"    "
	for lumi in by_file[filename]["lumis present"]:
		line += str(lumi)+","
	line += "    "
	for trigger in by_file[filename]["triggers"].keys():
		line += trigger+","+str(by_file[filename]["triggers"][trigger]["present"])+","
		line += str(np.mean(by_file[filename]["triggers"][trigger]["prescale1"]))+","
		line += str(np.mean(by_file[filename]["triggers"][trigger]["prescale2"]))+","
		line += str(by_file[filename]["triggers"][trigger]["fired"])+",,"
	line += "\n"
	w.write(line)

x = open("reg_by_lumi.txt","w")
x.write("lumi block    events    files present    triggers(present,fired,avg prescale val)\n")
for lumi in by_lumi.keys():
	line = str(lumi)+"    "
	line += str(by_lumi[lumi]["events"])+"    "
	for filename in by_lumi[lumi]["files present"]:
		line += str(filename)+","
	line += "    "
	for trigger in by_lumi[lumi]["triggers"].keys():
		line += trigger+","+str(by_lumi[lumi]["triggers"][trigger]["present"])+","
		line += str(np.mean(by_lumi[lumi]["triggers"][trigger]["prescale1"]))+","
		line += str(np.mean(by_lumi[lumi]["triggers"][trigger]["prescale2"]))+","
		line += str(by_lumi[lumi]["triggers"][trigger]["fired"])+",,"
	line += "\n"
	x.write(line)
