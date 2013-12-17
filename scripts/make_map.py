import os
import atexit
import sys
import subprocess
from time import sleep
from shlex import split
from signal import SIGINT

class LaunchMapping:
    def __init__(self):
        self.localization_p = None
        self.octomap_p = None

    def confirm_action_with_text(self, f, text):
        done = False
        while not done:
            input = raw_input()
            if input.lower().strip() == text:
                f()
                done = True
            else:
                print "didn't understand that. try again"
    def check_directory(self, path):
        expand_path = os.path.expanduser(path)
        return os.path.isdir(expand_path)

    def launch_gmapping(self):
        cmd = 'roslaunch mapmaking slam_gmapping.launch'
        self.gmapping_p = subprocess.Popen(split(cmd), stdout=subprocess.PIPE)
        sleep(1)
        return

    def kill_gmapping(self):
        print "saving map"
        cmd = 'rosrun map_server map_saver'
        subprocess.call(split(cmd))
        self.move_map_files(directory, file_stem)
        sleep(1)
        self.gmapping_p.send_signal(SIGINT)
        print "done killing gmapping"

    # replaces the pgm file that the yaml points with the stem string
    def move_map_files(self, directory, stem):
        f = open('map.yaml', 'r')
        self.new_yaml = os.path.join(directory, '%s.yaml' % stem)
        output = open(self.new_yaml, 'w')
        lines = f.readlines()
        for line in lines:
            if "map.pgm" in line:
                output.write(line.replace('map.pgm', '%s.pgm' % stem))
            else:
                output.write(line)
        output.close()
        subprocess.call(split('rm map.yaml'))
        
        new_pgm = os.path.join(directory, '%s.pgm' % stem)
        cmd = 'mv map.pgm %s' % new_pgm
        subprocess.call(split(cmd))
        print "wrote the following files:"
        print new_pgm
        print self.new_yaml

    def atexit_handle(self):
        self.gmapping_p.send_signal(SIGINT)
        if self.localization_p:
            self.localization_p.send_signal(SIGINT)
        if self.octomap_p:
            self.octomap_p.send_signal(SIGINT)

    def launch_localization(self):
        print "launching localization..."
        cmd = 'roslaunch mapmaking localization.launch map_name:=%s' % self.new_yaml
        self.localization_p = subprocess.Popen(split(cmd),
                                               stdout=subprocess.PIPE)

    def launch_octomap(self):
        print "launching octomap"
        cmd = 'roslaunch mapmaking octomap_mapping.launch'
        self.octomap_p = subprocess.Popen(split(cmd), stdout=subprocess.PIPE)

    def waiter(self):
        pass

    def save_octomap(self, directory, stem):
        filename = os.path.join(directory, '%s.bt'% stem)
        cmd = 'rosrun octomap_server octomap_saver %s' % filename
        subprocess.call(split(cmd))
        print "saved %s octomap file" % filename

if __name__ == "__main__":
    directory = sys.argv[1]
    file_stem = sys.argv[2]

    mapping = LaunchMapping()
    atexit.register(mapping.atexit_handle)
    if not mapping.check_directory(directory):
        print "%s is not a valid path" % sys.argv[1]
        exit(1)
    mapping.launch_gmapping()
    print "gmapping launched. please build the map, then type 'done'."
    mapping.confirm_action_with_text(mapping.kill_gmapping, 'done')

    sleep(1)
    mapping.launch_localization()
    print "when finished localizing the robot, type 'done'"
    mapping.confirm_action_with_text(mapping.launch_octomap, 'done')
    print "when done mapping the room, type 'done'"
    mapping.confirm_action_with_text(mapping.waiter, 'done')
    mapping.save_octomap(directory, file_stem)
