import sys
import numpy as np
import gc
import os
gc.collect()



lumibyls = sys.argv[1]
input_dir = sys.argv[2]
data_type = sys.argv[3]
data_year = sys.argv[4]
trigger_cat = sys.argv[5]
version = "6"

def format2_6(string,num):
	return " "*(num-len(string))+ string

def assure_path_exists(path):
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
                os.makedirs(dir)


def runs_to_lumi(filename):
	lumibyls_data = open(filename)
	lines = lumibyls_data.readlines()
	split_lines = [line.split(",") for line in lines][2:]
	
	char = ""
	run_lumi_dict =  {}
	i = 0
	while char != "#":
		run = split_lines[i][0].strip().split(":")[0]
		lumi = split_lines[i][1].strip().split(":")[0]
		rlumi_delivered = float(split_lines[i][5])
		rlumi_recorded = float(split_lines[i][6])
		run_lumi_dict[(run,lumi)] = (rlumi_delivered,rlumi_recorded)

		i += 1
		try:
			char = split_lines[i][0][0]
		except: pass
	return run_lumi_dict		


assure_path_exists(input_dir.replace("MOD","stats2")+"/")
run_lumi_dict = runs_to_lumi(lumibyls)


for mod_orig in os.listdir(input_dir):
	total_lum_del = 0.0
	total_lum_rec = 0.0
	lumi_info = {}
	total_events = 0
	valid_events = 0
	good_lumis = []
# counters for what to write to stats2
	with open(input_dir+"/"+mod_orig, "rb") as mod_file:
	    for line in mod_file: 
		if ("#" not in line.split()) and ("Cond" in line.split()):
			# corresponds to 1 event
			total_events += 1
			run = line.split()[1]
			lumiBlock = line.split()[6]
			if data_type == "Data":
				try: 
					luminosity = run_lumi_dict[(run,lumiBlock)]
					is_valid = True
				except KeyError:
					is_valid = False 
			if data_type == "Sim":
				is_valid = True
				cross_section = line.split()[8]
			if is_valid: valid_events += 1
			# summing up integrated lumi if the block has not already been counted
			if data_type == "Data":
				if (run,lumiBlock) not in good_lumis:
					try:
						total_lum_del += run_lumi_dict[(run,lumiBlock)][0]
						total_lum_rec += run_lumi_dict[(run,lumiBlock)][1]
						good_lumis.append((run,lumiBlock))
					except:
						pass


				if (run,lumiBlock) not in lumi_info.keys():
					lumi_info[(run,lumiBlock)] = {"events":1,"valid":0}
					if is_valid: lumi_info[(run,lumiBlock)]["valid"] = 1
				else:
					lumi_info[(run,lumiBlock)]["events"] += 1
			if data_type == "Sim":
				if (run,lumiBlock) not in good_lumis:
					good_lumis.append((run,lumiBlock))
					
				if (run,lumiBlock) not in lumi_info.keys():
					lumi_info[(run,lumiBlock)] = {"events":1,"valid":0}
					if is_valid: lumi_info[(run,lumiBlock)]["valid"] = 1
				else:
					lumi_info[(run,lumiBlock)]["events"] += 1


			
	mod_file.close()
	
	# actually writes stats2
	w = open(input_dir.replace("MOD","stats2")+"/"+str(mod_orig[-40:-4])+".stats2","w")
	w.write("BeginFile Version " + version + " CMS_" + data_year + " " + data_type + " " + trigger_cat + "\n")
	if data_type == "Data":
		w.write("#   File"+format2_6("Filename",40)+format2_6("TotalEvents",15)+format2_6("ValidEvents",15)+format2_6("IntLumiDel",15)+format2_6("IntLumiRec",15)+"\n")
		w.write("    File"+format2_6(str(mod_orig[-40:-4]),40)+format2_6(str(total_events),15)+format2_6(str(valid_events),15)+format2_6("{0:.3f}".format(total_lum_del),15)+format2_6("{0:.3f}".format(total_lum_rec),15)+"\n")
		w.write("#  Block"+format2_6("RunNum",15)+format2_6("LumiBlock",10)+format2_6("Events",10)+format2_6("Valid?",10)+format2_6("IntLumiDel",15)+format2_6("IntLumiRec",15)+"\n")
		for lumi in sorted(sorted(lumi_info.keys(),key=lambda tup: tup[1]),key=lambda tup: tup[0]):
			try:
				w.write("   Block"+format2_6(str(lumi[0]),15)+format2_6(str(lumi[1]),10)+format2_6(str(lumi_info[lumi]["events"]),10)+format2_6(str(lumi_info[lumi]["valid"]),10)+format2_6("{0:.3f}".format(run_lumi_dict[lumi][0]),15)+format2_6("{0:.3f}".format(run_lumi_dict[lumi][1]),15)+"\n")
			except KeyError:
				w.write("   Block"+format2_6(str(lumi[0]),15)+format2_6(str(lumi[1]),10)+format2_6(str(lumi_info[lumi]["events"]),10)+format2_6(str(lumi_info[lumi]["valid"]),10)+format2_6("0.000",15)+format2_6("0.000",15)+"\n")
	if data_type == "Sim":
		w.write("#   File"+format2_6("Filename",40)+format2_6("TotalEvents",15)+format2_6("ValidEvents",15)+format2_6("CrossSection",15)+"\n")
		w.write("    File"+format2_6(str(mod_orig[-40:-4]),40)+format2_6(str(total_events),15)+format2_6(str(total_events),15)+format2_6("{0:.3f}".format(float(cross_section)),15)+"\n")
		w.write("#  Block"+format2_6("RunNum",15)+format2_6("LumiBlock",10)+format2_6("Events",10)+format2_6("Valid?",10)+format2_6("CrossSection",20)+"\n")
		for lumi in sorted(sorted(lumi_info.keys(),key=lambda tup: tup[1]),key=lambda tup: tup[0]):
			w.write("     Block"+format2_6(str(lumi[0]),15)+format2_6(str(lumi[1]),10)+format2_6(str(lumi_info[lumi]["events"]),10)+format2_6("1",10)+format2_6("{0:.3f}".format(float(cross_section)),34)+"\n")
	
	
	w.write("EndFile\n")

	w.close()
