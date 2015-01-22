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

    args = parser.parse_args()

    if not os.path.exists(PATH):
        os.makedirs(PATH)

    min_distance_0 = 0
    MAX_RANGE = 6000
    IP = args.robot_ip
    PORT = 9559
    vd = ALProxy("ALVideoDevice", IP, PORT)
    name = vd.subscribeCamera("AsusF", 2, 1, 17, 20)
    if name == "":
        print "Could not subscribe to ALVideoDevice"
        import sys
        sys.exit(0)

    im = None
    alimage = vd.getImageRemote(name)
    if(alimage is None):
        print "Error..."
        time.sleep(1)
    width = alimage[0]
    height = alimage[1]
    data = alimage[6]

    depth = numpy.array(array.array("H", data)).reshape(height, width)
    if im is None:
        depth[0, 0] = MAX_RANGE
        im = pyplot.imshow(depth, cmap="gist_stern")
    else:
        im.set_data(depth)
    try:
        while(True):
            date_log = datetime.datetime.now().strftime("%H-%M-%S_%f")
            pyplot.savefig("./" + PATH + "/" + date_log + "_" + name,
                           dpi=None, format='eps')

    except KeyboardInterrupt:
        vd.unsubscribe(name)
        print "Unsubscribed client " + name + " from ALVideoDevice"

if __name__ == '__main__':
    main()
