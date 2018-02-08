import sys

file_to_count = sys.argv[1]

numevents = 0

print sun([int(x) for x in open(file_to_count).read().split()[::2]])

