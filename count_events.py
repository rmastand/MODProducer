import sys
file_to_count = sys.argv[1]
print sum([int(x) for x in open(file_to_count).read().split()[::2]])

