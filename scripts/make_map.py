import os
import sys
import subprocess
from shlex import split

def check_directory(path):
    expand_path = os.path.expanduser(path)
    return os.path.isdir(expand_path)

def launch_gmapping():
    cmd = 'roslaunch mapmaking slam_gmapping.launch'
    gmapping_p = subprocess.Popen(split(cmd))
    sleep(1)
    return

if __name__ == "__main__":
    if not check_directory(sys.argv[1]):
        print "%s is not a valid path" % sys.argv[1]
        exit(1)
    print "gmapping launched. please build the map."
