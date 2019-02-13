import sys
import numpy as np

file = sys.argv[1]

total_lumin = 0

for line in open(file,"r").readlines():
  rec_lumi = line.split(3)
  print rec_lumi

