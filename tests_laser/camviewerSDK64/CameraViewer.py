'''
Version : 1
File    : cameraTest.py
Created : 24.06.2014
Author  : Ahmed Lazreg, Jorg Ziegler
          (c) 2014 Aldebaran Robotics. All rights reserved.

Description: This example show how to use the python binding
             to CameraViewer internal. It instanciates a Camera
             class and call some of its methods

Requirement: Python 2.7.3, Python binding modules to CameraViewer
'''

from pybinding import *
from cvClasses import *
import time
import os

CAMERA_VIEWER_BINDING_LIB_PATH = '/home/amartin/workspace/hardware-test/hw-tests/tests_laser/camviewerSDK64/libcameraViewer.so'


def getImage(self):
    return 9


def camera_connect():
    libInitialize(CAMERA_VIEWER_BINDING_LIB_PATH)

    cameraFront = Camera(BoardLocationEnum.kBoardFront)
    print "Trying to connect to Front camera. Please wait ..."
    # this method takes about 10 seconds because of USB enumeration process
    # and automatic listing of all processor registers
    cameraFront.connect()
    return cameraFront


def save_image(cameraFront, path, name):
    if cameraFront.isConnected():
        print path
        path1 = path + "/"
        try:
            os.makedirs(os.path.dirname(path1))
        except:
            pass

        for laserId in LaserIdEnum.laserIdSet:
            cameraFront.setLaser(laserId)
            # after having sent a command to a laserBoard, always give 1 sec to
            # let sensor update its internal state
            time.sleep(1)
                          # general rule: time between two commands sent to a
                          # sensor must be at least 1 sec

            imageFileName = path + "/image" + name + "-%s.bmp" % LaserIdEnum.laserIdAsStr(
                laserId)  # using default values (OverlayON and ZoomFactor = 3)
            # cameraFront.saveImageToFile(imageFileName,
            # ImageSaveOptionsEnum.kOpt_OverlayOff, 3)  # value 3 is zoomFactor
            result = cameraFront.saveImageToFile(imageFileName)
            if result == RESULT_OK:
                print "Image captured and saved to file %s" % imageFileName
            else:
                print "Error saving image to file %s. ErrorCode(%d)" % (imageFileName, result)


def camera_disconnect(cameraFront):
    cameraFront.disconnect()
