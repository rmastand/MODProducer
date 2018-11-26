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
assure_path_exists(mod_file_dir.replace("MOD","trigl")+"/")

for file in os.listdir(mod_file_dir):
	trig_dict = {}
	tot_present = 0
	tot_valid = 0
	# we'll use this later for calculate the total delivered and recorded luminosities
	good_lumis = []
	print file

	with open(mod_file_dir+"/"+file, "rb") as mod_file:
		for line in mod_file: 
	

			# keeps track of the run, lumiBlock
			# this should signal each separate event
			if (("Cond" in line.split()) or ("SCond" in line.split())) and ("#" not in line.split()):
				run,lumiBlock = line.split()[1],line.split()[3]
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

	
	
	
	statsFile = open(mod_file_dir.replace("MOD","stats")+"/"+str(file[-40:-4])+".stats")
	lines = statsFile.readlines()
	statsFile.close()
	
	w = open(mod_file_dir.replace("MOD","trigl")+"/"+str(file[-40:-4])+".trigl","w")
	w.writelines([item for item in lines[:-1]])
	
	if data_type == "Data":
		w.write("#        Trig"+format2_6("Name",40)+format2_6("Present",13)+format2_6("Valid",12)+format2_6("Fired",12)+format2_6("EffLumiDel",13)+format2_6("EffLumiRec",20)+format2_6("AvePrescale",14)+"\n")
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

			w.write("         Trig"+format2_6(trig,40)+format2_6(str(trig_dict[trig]["present"]),13)+format2_6(str(trig_dict[trig]["present_valid"]),12)+format2_6(str(trig_dict[trig]["present_valid_fired"]),12)+format2_6(str("{0:.3f}".format(np.sum(eff_lum_del))),13)+format2_6(str("{0:.3f}".format(np.sum(eff_lum_rec))),20)+format2_6(str("{0:.3f}".format(np.mean(trig_dict[trig]["avg_prescale"]))),14)+"\n")	
		
	if data_type == "Sim":
		w.write("#       STrig"+format2_6("Name",40)+format2_6("Present",15)+format2_6("Valid",15)+format2_6("Fired",20)+"\n")
		for trig in trig_dict.keys():
			w.write("        STrig"+format2_6(trig,40)+format2_6(str(trig_dict[trig]["present"]),15)+format2_6(str(trig_dict[trig]["present_valid"]),15)+format2_6(str(trig_dict[trig]["present_valid_fired"]),20)+"\n")	
	w.write("EndFile")
	w.close()

