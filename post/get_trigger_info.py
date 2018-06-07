import sys
import os
import numpy as np

mod_file_dir = sys.argv[1]
skimmed_lumibyls = sys.argv[2]
data_type = sys.argv[3]

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
assure_path_exists(mod_file_dir.replace("MOD","trig")+"/")


for file in os.listdir(mod_file_dir):
	trig_dict = {}
	tot_present = 0
	tot_valid = 0
	# we'll use this later for calculate the total delivered and recorded luminosities
	good_lumis = []
	i = 0
	with open(mod_file_dir+"/"+file, "rb") as mod_file:
		for line in mod_file: 
			if i == 0:
				first_line = line
			i += 1

			# keeps track of the run, lumiBlock
			# this should signal each separate event
			if ("Cond" in line.split()) and ("#" not in line.split()):
				run,lumiBlock = line.split()[1],line.split()[6]
				tot_present += 1

				if (is_lumi_valid((run,lumiBlock),lumiId_to_lumin_dict)) and (data_type == "Data"):
					tot_valid += 1		
					if (run,lumiBlock) not in good_lumis:
						good_lumis.append((run,lumiBlock))
				if data_type == "Sim":
					tot_valid += 1

			if ("Trig" in line.split()) and ("#" not in line.split()):
				# all within 1 event
				# given line: [Trig identifier, trig name, prescale1, prescale2, fired?]
				if line.split()[1] not in trig_dict.keys():
					trig_dict[line.split()[1]] = {"present":1,
								      "present_valid":0,	    
								      "present_valid_fired":0,
								      # calc average over all VALID and FIRED EVENTS
								      "avg_prescale":[],
								      # no repetitions
								      "good_lumis":[],
								      # corresponds to the prescale for a given GOOD LUMI BLOCK
								      "good_prescales":[]
								     }
					if data_type == "Data":
						trig_dict[line.split()[1]]["present_valid"] = is_lumi_valid((run,lumiBlock),lumiId_to_lumin_dict)
						trig_dict[line.split()[1]]["present_valid_fired"] = is_lumi_valid((run,lumiBlock),lumiId_to_lumin_dict) and int(line.split()[4])
						if trig_dict[line.split()[1]]["present_valid_fired"]==1:
							trig_dict[line.split()[1]]["avg_prescale"].append(float(line.split()[2])*float(line.split()[3]))
						if is_lumi_valid((run,lumiBlock),lumiId_to_lumin_dict) and ((run,lumiBlock) not in trig_dict[line.split()[1]]["good_lumis"]):
							trig_dict[line.split()[1]]["good_lumis"].append((run,lumiBlock))
							trig_dict[line.split()[1]]["good_prescales"].append(float(line.split()[2])*float(line.split()[3]))

					if data_type == "Sim":
						trig_dict[line.split()[1]]["present_valid"] = 1
						trig_dict[line.split()[1]]["present_valid_fired"] = int(line.split()[4])
						if trig_dict[line.split()[1]]["present_valid_fired"]==1:
							trig_dict[line.split()[1]]["avg_prescale"].append(float(line.split()[2])*float(line.split()[3]))
						if (run,lumiBlock) not in trig_dict[line.split()[1]]["good_lumis"]:
							trig_dict[line.split()[1]]["good_lumis"].append((run,lumiBlock))
							trig_dict[line.split()[1]]["good_prescales"].append(float(line.split()[2])*float(line.split()[3]))

				else:
					if data_type == "Data":
						trig_dict[line.split()[1]]["present"] += 1
						trig_dict[line.split()[1]]["present_valid"] += is_lumi_valid((run,lumiBlock),lumiId_to_lumin_dict)
						trig_dict[line.split()[1]]["present_valid_fired"] += is_lumi_valid((run,lumiBlock),lumiId_to_lumin_dict) and int(line.split()[4])
						if (is_lumi_valid((run,lumiBlock),lumiId_to_lumin_dict) and int(line.split()[4]))==1:
							trig_dict[line.split()[1]]["avg_prescale"].append(float(line.split()[2])*float(line.split()[3]))
						if is_lumi_valid((run,lumiBlock),lumiId_to_lumin_dict) and ((run,lumiBlock) not in trig_dict[line.split()[1]]["good_lumis"]):
							trig_dict[line.split()[1]]["good_lumis"].append((run,lumiBlock))
							trig_dict[line.split()[1]]["good_prescales"].append(float(line.split()[2])*float(line.split()[3]))
					if data_type == "Sim":
						trig_dict[line.split()[1]]["present"] += 1
						trig_dict[line.split()[1]]["present_valid"] += 1
						trig_dict[line.split()[1]]["present_valid_fired"] += int(line.split()[4])
						if int(line.split()[4])==1:
							trig_dict[line.split()[1]]["avg_prescale"].append(float(line.split()[2])*float(line.split()[3]))
						if (run,lumiBlock) not in trig_dict[line.split()[1]]["good_lumis"]:
							trig_dict[line.split()[1]]["good_lumis"].append((run,lumiBlock))
							trig_dict[line.split()[1]]["good_prescales"].append(float(line.split()[2])*float(line.split()[3]))


	w = open(mod_file_dir.replace("MOD","trig")+"/"+str(file[-40:-4])+".trig","w")
	w.write(first_line.replace("Event","File"))
	tot_lumi_del = 0.
	tot_lumi_rec = 0.
	for lumi in good_lumis:
		tot_lumi_del += lumiId_to_lumin_dict[lumi][0]
		tot_lumi_rec += lumiId_to_lumin_dict[lumi][1]
		
	
		
	w.write("#   File"+format2_6("Filename",40)+format2_6("Present",10)+format2_6("Valid",10)+format2_6("LuminDel",15)+format2_6("LuminRec",15)+"\n")
	w.write("    File"+format2_6(str(file[-40:-4]),40)+format2_6(str(tot_present),10)+format2_6(str(tot_valid),10)+format2_6("{0:.3f}".format(tot_lumi_del),15)+format2_6("{0:.3f}".format(tot_lumi_rec),15)+"\n")


	w.write("#   Trig"+format2_6("Name",40)+format2_6("Present",10)+format2_6("Valid",10)+format2_6("Fired",10)+format2_6("AvePrescale",15)+format2_6("EffLuminDel",15)+format2_6("EffLuminRec",15)+"\n")
	for trig in trig_dict.keys():
		eff_lum_del = []
		eff_lum_rec = []
		for i in range(len(trig_dict[trig]["good_lumis"])):
			try:
				eff_lum_del.append(lumiId_to_lumin_dict[trig_dict[trig]["good_lumis"][i]][0]/trig_dict[trig]["good_prescales"][i])
				eff_lum_rec.append(lumiId_to_lumin_dict[trig_dict[trig]["good_lumis"][i]][1]/trig_dict[trig]["good_prescales"][i])
			except KeyError:
				eff_lum_del.append(0.000)
				eff_lum_rec.append(0.000)

		w.write("    Trig"+format2_6(trig,40)+format2_6(str(trig_dict[trig]["present"]),10)+format2_6(str(trig_dict[trig]["present_valid"]),10)+format2_6(str(trig_dict[trig]["present_valid_fired"]),10)+format2_6(str("{0:.3f}".format(np.mean(trig_dict[trig]["avg_prescale"]))),15)+format2_6(str("{0:.3f}".format(np.sum(eff_lum_del))),15)+format2_6(str("{0:.3f}".format(np.sum(eff_lum_rec))),15)+"\n")	
	w.write("EndFile\n")
	w.close()


