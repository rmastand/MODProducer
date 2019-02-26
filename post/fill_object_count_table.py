import numpy as np
import sys

mod_file = sys.argv[1]
lumibyls_file = sys.argv[2]


def read_lumi_by_ls(lumibyls_file):
	"""
	returns two dicts with keys = (run,lumiBlock)
	1st values: gps times
	2nd values: (lumi_delivered, lumi_recorded)
	"""
	lumibyls = open(lumibyls_file)
	lines =  lumibyls.readlines()
	split_lines = [line.split(",") for line in lines][2:]
	char = ""
	lumi_id_to_gps_times = {}
	lumi_id_to_lumin = {}
	time_series_all = []
	lumin_all = []
	i = 0
	while char !="#":
		run = split_lines[i][0].split(":")[0]
		lumi = split_lines[i][1].split(":")[0]
		date = split_lines[i][2].split(" ")[0]
		tim = split_lines[i][2].split(" ")[1]
		mdy = [int(x) for x in date.split("/")]
		hms = [int(x) for x in tim.split(":")]
		lumi_id_to_lumin[(run,lumi)] = (float(split_lines[i][5]),float(split_lines[i][6]))
		i += 1
		try:
			char = split_lines[i][0][0]
		except: pass
	return lumi_id_to_lumin



lumi_id_to_lumin = read_lumi_by_ls(lumibyls_file)


object_id_dict = {}
object_id_dict_1Gev = {}

lumi_is_valid = 5


with open(mod_file, "r") as mod_file:
  for line in mod_file:  
    if ("Cond" in line.split()) and ("#" not in line.split()): # getting the lumiblock info
      run = line.split()[1]
      lumi = line.split()[3]
      try: 
        p = lumi_id_to_lumin[(run,lumi)]
        lumi_is_valid = 1
      except KeyError: 
        lumi_is_valid = 0
        print "not"
    if ("PFC" in line.split()) and ("#" not in line.split()): # getting the PFC info
      pdgid = int(line.split()[5])
      pt = np.sqrt(float(line.split()[1])**2 + float(line.split()[2])**2)
      if lumi_is_valid:
        try: object_id_dict[pdgid] += 1
        except KeyError: object_id_dict[pdgid] = 1
        if pt > 1:
          try: object_id_dict_1Gev[pdgid] += 1
          except KeyError: object_id_dict_1Gev[pdgid] = 1
            
print object_id_dict
print 
print object_id_dict_1Gev
       
