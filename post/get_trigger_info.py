import sys
import os

mod_file_dir = sys.argv[1]
skimmed_lumibyls = sys.argv[2]

trig_dict = {}

def get_lumiId_to_lumin(skim_filename):
	lumiId_to_lumin_dict = {}
	with open(skim_filename,"r") as skim_file:
		for line in skim_file:
			lumi_id,lumi_del,lumi_rec = line.split()
			lumiId_to_lumin_dict[(lumi_id.split("_")[0],lumi_id.split("_")[1])] = lumi_del,lumi_rec
	return lumiId_to_lumin_dict
		
def is_lumi_valid(lumi_id,lumiId_to_lumin_dict):
	try:
		luminosity = lumiId_to_lumin_dict[lumi_id]
		return 1
	except KeyError:
		return 0

lumiId_to_lumin_dict = get_lumiId_to_lumin(skimmed_lumibyls)
	


for file in os.listdir(mod_file_dir):
	with open(mod_file_dir+"/"+file, "rb") as mod_file:
		for line in mod_file: 
			# keeps track of the run, lumiBlock
			if ("Cond" in line.split()) and ("#" not in line.split()):
				run,lumiBlock = line.split()[1],line.split()[6]

		
			if ("Trig" in line.split()) and ("#" not in line.split()):
				# given line: [Trig identifier, trig name, prescale1, prescale2, fired?]
				if line.split()[1] not in trig_dict.keys():
					trig_dict[line.split()[1]] = {"present":1,"present_valid":is_lumi_valid((run,lumiBlock),lumiId_to_lumin_dict),"present_fired":int(line.split()[4]),"present_valid_fired":is_lumi_valid((run,lumiBlock),lumiId_to_lumin_dict) and int(line.split()[4])}
					print trig_dict[line.split()[1]]
				else:
					trig_dict[line.split()[1]]["present"] += 1
					trig_dict[line.split()[1]]["present_valid"] += is_lumi_valid((run,lumiBlock),lumiId_to_lumin_dict)
					trig_dict[line.split()[1]]["present"] += int(line.split()[4])
					trig_dict[line.split()[1]]["present"] += is_lumi_valid((run,lumiBlock),lumiId_to_lumin_dict) and int(line.split()[4])
for trig in trig_dict.keys():
	print trig
	print trig_dict[trig]
	print

