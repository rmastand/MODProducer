import sys
import os

mod_file_dir = sys.argv[1]

trig_dict = {}

for file in os.listdir(mod_file_dir):
	with open(mod_file_dir+"/"+file, "rb") as mod_file:
		for line in mod_file: 
			if ("Trig" in line.split()) and ("#" not in line.split()):
				print line.split()
      
