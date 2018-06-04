import sys
import os

stats_dir = sys.argv[1]
stats2_dir = sys.argv[2]


for file in os.listdir(stats_dir):
  print file
  
