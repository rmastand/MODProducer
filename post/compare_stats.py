import sys
import os

stats_dir = sys.argv[1]
stats2_dir = sys.argv[2]

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

overlap = [x for x in in_stats if x in in_stats2]

print "files in registry but without mod:"
for i in no_matches[0]: print i
print
print "files with mod but not in registry (should be none):"
for i in no_matches[1]: print i
print

print overlap
print type(overlap)





