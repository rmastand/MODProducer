import sys
import os
import subprocess

stats_dir = sys.argv[1]
stats2_dir = sys.argv[2]
error_log = sys.argv[3]

in_stats = []
in_stats2 = []


def returnNotMatches(stats, stats2):
    # in stats but not in stats2, in stats2 but not in stats
    return [[x for x in stats if x not in stats2], [x for x in stats2 if x not in stats]]


for file in os.listdir(stats_dir):
  in_stats.append(file[:-6])
for file in os.listdir(stats2_dir):
  in_stats2.append(file[:-7])
no_matches = returnNotMatches(in_stats,in_stats2)

print "files in registry but without mod:"
for i in no_matches[0]: print i
print
print "files with mod but not in registry (should be none):"
for i in no_matches[1]: print i
print


errorlog = open(error_log,"w")

overlap = [x for x in in_stats if x in in_stats2]

for file in overlap:
    with open(stats_dir+"/"+file+".stats", 'r') as file1:
        with open(stats2_dir+"/"+file+".stats2", 'r') as file2:
            difference = set(file1).difference(file2)
    difference.discard('\n')
    
    if not len(difference) == 0:
        errorlog.write(file+"\n")
        for line in difference:
            errorlog.write(line)
       
errorlog.close()


    
    




