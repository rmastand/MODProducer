import sys
import os
import numpy as np

mod_file_dir = sys.argv[1]
skimmed_lumibyls = sys.argv[2]

def format2_6(string,num):
	return " "*(num-len(string))+ string

def assure_path_exists(path):
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
                os.makedirs(dir)

def get_lumiId_to_lumin(skim_filename):
	lumiId_to_lumin_dict = {}
	with open(skim_filename,"r") as skim_file:
		for line in skim_file:
			lumi_id,lumi_del,lumi_rec = line.split()
			lumiId_to_lumin_dict[(lumi_id.split("_")[0],lumi_id.split("_")[1])] = float(lumi_del),float(lumi_rec)
	return lumiId_to_lumin_dict
		
def is_lumi_valid(lumi_id,lumiId_to_lumin_dict):
	try:
		luminosity = lumiId_to_lumin_dict[lumi_id]
		return 1
	except KeyError:
		return 0

lumiId_to_lumin_dict = get_lumiId_to_lumin(skimmed_lumibyls)
assure_path_exists(input_dir.replace("MOD","trig")+"/")


for file in os.listdir(mod_file_dir):
	trig_dict = {}
	with open(mod_file_dir+"/"+file, "rb") as mod_file:
		for line in mod_file: 
			# keeps track of the run, lumiBlock
			if ("Cond" in line.split()) and ("#" not in line.split()):
				run,lumiBlock = line.split()[1],line.split()[6]

		
			if ("Trig" in line.split()) and ("#" not in line.split()):
				# given line: [Trig identifier, trig name, prescale1, prescale2, fired?]
				if line.split()[1] not in trig_dict.keys():
					trig_dict[line.split()[1]] = {"present":1,
								      "present_valid":is_lumi_valid((run,lumiBlock),lumiId_to_lumin_dict),	    
								      "present_valid_fired":is_lumi_valid((run,lumiBlock),lumiId_to_lumin_dict) and int(line.split()[4]),
								      "avg_prescale":[],
								      "eff_lumin":[]
								     }
					if trig_dict[line.split()[1]]["present_valid_fired"]==1:
						trig_dict[line.split()[1]]["avg_prescale"].append(float(line.split()[2])*float(line.split()[3]))
						trig_dict[line.split()[1]]["eff_lumin"].append(lumiId_to_lumin_dict[(run,lumiBlock)]/(float(line.split()[2])*float(line.split()[3])))
					
				else:
					trig_dict[line.split()[1]]["present"] += 1
					trig_dict[line.split()[1]]["present_valid"] += is_lumi_valid((run,lumiBlock),lumiId_to_lumin_dict)
					trig_dict[line.split()[1]]["present_valid_fired"] += is_lumi_valid((run,lumiBlock),lumiId_to_lumin_dict) and int(line.split()[4])
					if (is_lumi_valid((run,lumiBlock),lumiId_to_lumin_dict) and int(line.split()[4]))==1:
						trig_dict[line.split()[1]]["avg_prescale"].append(float(line.split()[2])*float(line.split()[3]))
						trig_dict[line.split()[1]]["eff_lumin"].append(lumiId_to_lumin_dict[(run,lumiBlock)]/(float(line.split()[2])*float(line.split()[3])))
	
	w = open(input_dir.replace("MOD","trig")+"/"+str(mod_orig[-40:-4])+".trig","w")
	w.write("BeginFile Version " + "\n")
	w.write("#   File"+format2_6("Filename",40)+"\n")
	w.write("    File"+format2_6(str(mod_orig[-40:-4]),40)+"\n")


	w.write("#   Trig"+format2_6("Name",40)+format2_6("Present",10)+format2_6("Present+Valid",15)+format2_6("Present+Valid+Fired",20)+format2_6("AvePrescale",15)+format2_6("EffLumin",15)+"\n")
	for trig in trig_dict.keys():
		w.write("#   Trig"+format2_6(trig,40)+format2_6(str(trig_dict[trig]["present"]),10)+format2_6(str(trig_dict[trig]["present_valid"]),15)+format2_6(str(trig_dict[trig]["present_valid_fired"]),20)+format2_6(str(np.mean(trig_dict[trig]["avg_prescale"])),15)+format2_6(str(np.mean(trig_dict[trig]["eff_lumin"])),15)+"\n")	
	w.write("EndFile\n")
	w.close()

