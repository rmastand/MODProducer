import sys
import numpy as np

file = sys.argv[1]

total_lumin = 0

for line in open(file,"r").readlines()[1:]:
  rec_lumi = line.split()[3]
  total_lumin += float(rec_lumi)
  
print total_lumin

