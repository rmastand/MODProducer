import sys
import os

mod_file_dir = sys.argv[1]
skimmed_lumibyls = sys.argv[2]

trig_dict = {}

def get_lumiId_to_lumin(skim_filename):
	lumiId_to_lumin = {}
	with open(skim_filename,"r") as skim_file:
		for line in skim_file:
			lumi_id,lumi_del,lumi_rec = line.split()
			lumiId_to_lumin[(lumi_id.split("_")[0],lumi_id.split("_")[1])] = lumi_del,lumi_rec
	return lumiId_to_lumin
		
		
	
'''
for file in os.listdir(mod_file_dir):
	with open(mod_file_dir+"/"+file, "rb") as mod_file:
		for line in mod_file: 
			if ("Trig" in line.split()) and ("#" not in line.split()):
				print line.split()
      
'''

print get_lumiId_to_lumin(skimmed_lumibyls)
