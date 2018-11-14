import sys
import os
import numpy as np


skimmed_lumibyls = sys.argv[1]
data_type = sys.argv[2]
output_table = sys.argv[3]

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

all_mod_dirs = ["/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/MOD/12Oct2013-v1/10000/",
"/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/MOD/12Oct2013-v1/20000_a/",
"/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/MOD/12Oct2013-v1/20000_b/",
"/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/MOD/12Oct2013-v1/20000_c/",
"/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/MOD/12Oct2013-v1/20001/"]

all_mod_dirs = ["/Volumes/Seagate Backup Plus Drive/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/MOD/12Oct2013-v1/20001/"]

i = 0
for mod_file_dir in all_mod_dirs:
	for file in os.listdir(mod_file_dir):
		i += 1
		# contains: list of valid lumi blocks, list of eff lumi in that lumi block, list of prescale values in that lumi block
		# ensure that each lumi block is counted only once
		trig_dict = {}
		# we'll use this later for calculate the total delivered and recorded luminosities
		good_lumis = []
		print i

		with open(mod_file_dir+"/"+file, "rb") as mod_file:
			for line in mod_file: 

				# keeps track of the run, lumiBlock
				# this should signal each separate event
				if (("Cond" in line.split()) or ("SCond" in line.split())) and ("#" not in line.split()):
					run,lumiBlock = line.split()[1],line.split()[3]

				if ("Trig" in line.split()) and ("#" not in line.split()):
					# all within 1 event
					# given line: [Trig identifier, trig name, prescale1, prescale2, fired?]
					if line.split()[1][:-3] not in trig_dict.keys():
						trig_dict[line.split()[1][:-3]] = {
									      # no repetitions
									      "good_lumis":[],
							 			"good_lumin":[],
									      # corresponds to the prescale for a given GOOD LUMI BLOCK
									      "good_prescales":[]
									     }
						if data_type == "Data":
							if is_lumi_valid((run,lumiBlock),lumiId_to_lumin_dict):
								if (run,lumiBlock) not in trig_dict[line.split()[1][:-3]]["good_lumis"]:
									trig_dict[line.split()[1][:-3]]["good_lumis"].append((run,lumiBlock))
									trig_dict[line.split()[1][:-3]]["good_prescales"].append(float(line.split()[2])*float(line.split()[3]))
									trig_dict[line.split()[1][:-3]]["good_lumin"].append(lumiId_to_lumin_dict[(run,lumiBlock)][1]/(float(line.split()[2])*float(line.split()[3])))


					else:
						if data_type == "Data":
							if is_lumi_valid((run,lumiBlock),lumiId_to_lumin_dict):
								if (run,lumiBlock) not in trig_dict[line.split()[1][:-3]]["good_lumis"]:
									trig_dict[line.split()[1][:-3]]["good_lumis"].append((run,lumiBlock))
									trig_dict[line.split()[1][:-3]]["good_prescales"].append(float(line.split()[2])*float(line.split()[3]))
									trig_dict[line.split()[1][:-3]]["good_lumin"].append(lumiId_to_lumin_dict[(run,lumiBlock)][1]/(float(line.split()[2])*float(line.split()[3])))


						
w = open(output_table,"w")

if data_type == "Data":
	w.write(format2_6("Name",40)+format2_6("Eff Lumin Rec",13)+format2_6("Avg Prescale",12)+"\n")
	for trig in trig_dict.keys():	
		w.write(format2_6(trig,40)+format2_6(str(np.sum(trig_dict[trig]["good_lumin"]))[:10],13)+format2_6(str(np.mean(trig_dict[trig]["good_prescales"]))[:10],12)+"\n")	
w.write("EndFile")
w.close()


