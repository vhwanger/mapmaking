import os
import sys
import subprocess
from shlex import split
from signal import SIGINT

class LaunchMapping:
    def confirm_action_with_text(f, text):
        done = False
        while not done:
            input = raw_input()
            if input.lower().strip() == text:
                f()
                done = True
            else:
                print "didn't understand that. try again"
    def check_dmrectory(self, path):
        expand_path = os.path.expanduser(path)
        return os.path.isdir(expand_path)

    def launch_gmapping(self):
        cmd = 'roslaunch mapmaking slam_gmapping.launch'
        self.gmapping_p = subprocess.Popen(split(cmd))
        sleep(1)
        return

    def kill_gmapping(self):
        print "saving map"
        cmd = 'rosrun map_server map_saver'
        subprocess.call(split(cmd))
        self.gmapping_p.send_signal(SIGINT)

    # replaces the pgm file that the yaml points with the stem string
    def move_map_files(stem):
        f = open('map.yaml', 'r')
        output = open('%s.yaml' % stem, 'w')
        lines = f.readlines()
        for line in lines:
            if "map.pgm" in line:
                output.write(line.replace('map.pgm', '%s.pgm' % stem))
            else:
                output.write(line)
        output.close()
        subprocess.call(split('rm map.yaml'))

        cmd = 'mv map.pgm %s.pgm' % stem
        subprocess.call(split(cmd))

if __name__ == "__main__":
    directory = sys.argv[1]
    file_stem = sys.argv[2]

    mapping = LaunchMapping()
    if not check_directory(directory):
        print "%s is not a valid path" % sys.argv[1]
        exit(1)
    mapping.launch_gmapping()
    print "gmapping launched. please build the map, then type 'done'."
    mapping.confirm_action_with_text(mapping.kill_gmapping, 'done')

    move_map_files(file_stem)

