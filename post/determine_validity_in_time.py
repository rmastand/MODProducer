#first: order all the lumiblocks in run A


import numpy as np
import sys
import os
import datetime
import time
import csv

parsed_file_inpur_dir = sys.argv[1]
lumibyls_file = sys.argv[2]
run_alumi_file = sys.argv[3]

runA_runs = []
read_alumi_lines = open(run_alumi_file,"r").readlines()
for line in read_alumi_lines[4:]:
  char = line[0]
  if char != "+":
    runA_runs.append(line.split()[1].split(":")[0])
  else:
    break
print "Done reading in ALumi"

replicate each vector for each trigger as a line of 0s
go thorugh the lumibloks for each trigger, then index change to 1 if present
