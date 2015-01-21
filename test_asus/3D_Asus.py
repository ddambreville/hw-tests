from naoqi import ALProxy
from vision_definitions import *
import array
import numpy
from PIL import Image
import matplotlib.pyplot as pyplot
import time
import datetime
import ConfigParser
import argparse
import sys
import os


DEFAULT_IP = "127.0.0.1"
PATH = "img"


def main():
    """Read the configuration file and start logging."""
    parser = argparse.ArgumentParser(description="Log datas from ALMemory")

    parser.add_argument("-i", "--IP", dest="robot_ip", default=DEFAULT_IP,
                        help="Robot IP or name (default: 127.0.0.1)")

    parser.add_argument("-v", "--version", action="version",
                        version="%(prog)s 1.0")

    # parser.add_argument("-o", "--output", dest="output"
    #                   default=DEFAULT_OUTPUT)

    args = parser.parse_args()

    if not os.path.exists(PATH):
        os.makedirs(PATH)

    MAX_RANGE = 6000
    IP = args.robot_ip
    PORT = 9559
    vd = ALProxy("ALVideoDevice", IP, PORT)
    name = vd.subscribeCamera("AsusF", 2, 1, 17, 20)
    if name == "":
        print "Could not subscribe to ALVideoDevice"
        import sys
        sys.exit(0)

    try:
        im = None
        while(True):
            alimage = vd.getImageRemote(name)
            if(alimage is None):
                print "Error..."
                time.sleep(1)
                continue
            width = alimage[0]
            height = alimage[1]
            data = alimage[6]

            depth = numpy.array(array.array("H", data)).reshape(height, width)
            min_distance = 5000
            for k in range(0, height):
                for l in range(0, width):
                    current_value = depth[k][l]
                    if(current_value < min_distance and current_value != 0):
                        min_distance = current_value

            if im is None:
                depth[0, 0] = MAX_RANGE
                im = pyplot.imshow(depth, cmap="gist_stern")
            else:
                im.set_data(depth)

            date_log = datetime.datetime.now().strftime("%H-%M-%S_%f")
            pyplot.savefig("./img/" + date_log + "_" + name + "_dis_" +
                           str(min_distance), dpi=None, format='eps')

    except KeyboardInterrupt:
        vd.unsubscribe(name)
        print "Unsubscribed client " + name + " from ALVideoDevice"

    try:
        while(True):
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
