"""
Utility for creating a "registry" / "map" between event and run numbers against
which file each of those events should go to. This is done to maintain the same
local directory structure as in CMS' servers for all AOD files.

Usage:

1) First intialize CMS environment variables with:

cmsenv

2) Then, do:

python ./create_registry.py <input_path> <path_to_registry_file.dat>

where <input_path> is the path to the directory of your AOD files, and  
<path_to_registry_file.dat> is the path to a data file you'd like to write the
registry to. The file need not exist but it needs to be a path to a file and not
a directory.

"""

import subprocess
import os
from time import time
import sys
from skim_lumibyls import *

file_with_source_paths = sys.argv[1]
registry_file_path = sys.argv[2]
output_dir = sys.argv[3]
runbyls_file = sys.argv[4]
output_ls_file = sys.argv[5]
data_type = sys.argv[6]
data_year = sys.argv[7]




def assure_path_exists(path):
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
                os.makedirs(dir)


log_file_path = str(registry_file_path) + "_log.log"


def get_files_already_in_registry(registry_file):

    f = open(registry_file, "a")
    f.close()

    files = set()
    with open(registry_file) as f:
        for line in f:
            if len(line) > 1:
                files.add(line.split(" ")[2].split("\n")[0])
                print "Adding ", line.split(" ")

    return list(files)


def create_registry(path, log_file_path):

    files_already_processed = get_files_already_in_registry(registry_file_path)
    print "File already processed", files_already_processed

    files_to_process = []
    with open(path, 'r') as f:
        for line in f:
            files_to_process.append(line.strip("\n"))

    for root_file in sorted(files_to_process):
        stdoutdata, stderrdata = subprocess.Popen(
            ["cmsRun", "./reg/FilenameRun.py", root_file, registry_file_path, output_dir, output_ls_file, data_type, data_year]).communicate()

        if str(stderrdata) != "None":
            log_file = open(log_file_path, 'a')
            log_file.write(str(stderrdata) + "\n")
            log_file.close()
start = time()

runs_to_lumi(runbyls_file,output_ls_file)
assure_path_exists(output_dir)
create_registry(file_with_source_paths, log_file_path)

end = time()

print "Everything done in " + str(end - start) + " seconds!"
