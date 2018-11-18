import sys
import numpy as np

run_alumi_file = sys.argv[1]

read_alumi_lines = open(run_alumi_file,"r").readlines()
for line in read_alumi_lines[4:]:
  print line
  char = line[0]
  while char != "#":
    run = line.split()[1].split(":")[0]
    print run
