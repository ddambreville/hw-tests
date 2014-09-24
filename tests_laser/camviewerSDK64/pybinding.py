'''
Version : 1
File    : pybinding.py
Created : 24.06.2014
Author  : Ahmed Lazreg, Jorg Ziegler
          (c) 2014 Aldebaran Robotics. All rights reserved.

Description: Python binding to CameraViewer internals

Requirement: Python 2.7.3
'''

from ctypes import *
import numpy as np

import ctypes

hndLib = 0  # handle of the dynamically loaded lib

BYTE_PER_PIXEL = 2
IMAGE_WIDTH = 188
IMAGE_HEIGHT = 120
IMAGE_SIZE = IMAGE_WIDTH * IMAGE_HEIGHT
ARGB_IMAGE_BYTES_COUNT = 4  # four bytes per pixel
IMAGE_BYTES_COUNT = IMAGE_WIDTH * IMAGE_HEIGHT * ARGB_IMAGE_BYTES_COUNT

LaserImageType = c_ushort * (IMAGE_SIZE)
PInt = POINTER(c_int)


class LaserIdEnum(object):
    kNoLaser = -1
    kLaser1 = 0   # Horizontal
    kLaser2 = 1   # Vertical-Left
    kLaser3 = 2   # Shovel
    kLaser4 = 3   # Vertical-Right
    laserIdSet = [kLaser2, kLaser4]
    laserId2Str = ["Horizontal", "Vertical-Left", "Shovel", "Vertical-Right"]

    @staticmethod
    def laserIdAsStr(laserId):
        assert (laserId in LaserIdEnum.laserIdSet)
        if laserId == LaserIdEnum.kNoLaser:
            return "Background"
        else:
            return LaserIdEnum.laserId2Str[laserId]


class BoardLocationEnum:
    kBoardUnknown = 0,
    kBoardFront = 1
    kBoardLeft = 2
    kBoardRight = 3
    boardLocationSet = [kBoardFront, kBoardLeft, kBoardRight]


def libInitialize(dllFilePath):
    # todo: pass the lib path as param and initialize the lib here
    global hndLib
    hndLib = ctypes.CDLL(dllFilePath)
    # todo: check if hndLib is not null ptr
    hndLib.cameraGetIntegrationTime.restype = ctypes.c_float
    hndLib.cameraGetRegisterName.restype = ctypes.c_char_p


''' Creates the camera object,
@param  boardLoc : any value from boardLocationEnum
@return handle to the camera object created
'''


def cameraCreate(boardLoc):
    assert(boardLoc in BoardLocationEnum.boardLocationSet)
    return hndLib.cameraCreate(boardLoc)


def cameraDestroy(hndCamera):
    hndLib.cameraDestroy(hndCamera)


def cameraGetNumLaser(hndCamera):
    return hndLib.cameraGetNumLaser(hndCamera)


def cameraConnect(hndCamera):
    return hndLib.cameraConnect(hndCamera)


def cameraDisconnect(hndCamera):
    hndLib.cameraDisconnect(hndCamera)


def cameraIsConnected(hndCamera):
    return hndLib.cameraIsConnected(hndCamera)


def cameraGetBoardLocation(hndCamera):
    loc = hndLib.cameraGetBoard(hndCamera)
    assert (loc in BoardLocationEnum.boardLocationSet)
    return BoardLocationEnum.boardLocationSet[loc]


def cameraGetImage(hndCamera):
    image = LaserImageType(0, 0, 0)
    hndLib.cameraGetImage(hndCamera, pointer(image))
    src16 = np.frombuffer(image, 'ushort', IMAGE_SIZE)
                          # create a flat/1D numpy array (16bit)
    # src16 = np.frombuffer(image, np.uint32, IMAGE_SIZE) # create a flat/1D
    # numpy array (16bit)
    img = np.zeros(IMAGE_SIZE, dtype='uint8')
                   # create a flat/1D numpy array (greyscale, 8bit)

    # convert to 2D image array
    img = img.reshape((IMAGE_HEIGHT, IMAGE_WIDTH))
    return img


class ImageSaveOptionsEnum(object):
    kOpt_OverlayOff = 0x1 << 0
    kOpt_OverlayOn = 0x1 << 1


RESULT_OK = 1
RESULT_ERR_IMAGE_EMPTY = 2
RESULT_ERR_SAVING_IMAGE_FILE = 3
RESULT_ERR_INVALID_SCALE_FACTOR = 4


def cameraSaveImageToFile(hndCamera, fileName, options, imageScaleFactor=3):
    return hndLib.cameraSaveImage(hndCamera, fileName, options, imageScaleFactor)


def cameraGetFrameNumber(hndCamera):
    return hndLib.cameraGetFrameNumber(hndCamera)


def cameraGetProcessorRegister(hndCamera, regIndex):
    regContent = c_int(0)
    hndLib.cameraGetRegister(hndCamera, c_int(regIndex), byref(regContent))
    # todo: pass the value byRef and return the error code from this function
    return regContent.value


def cameraGetProcessorRegisterByName(hndCamera, regName):
    regContent = c_int(0)
    hndLib.cameraGetRegisterByName(hndCamera, regName, byref(regContent))
    # todo: pass the value byRef and return the error code from this function
    return regContent.value


def cameraGetIntegrationTime(hndCamera):
    return hndLib.cameraGetIntegrationTime(hndCamera)


def cameraSetLaser(hndCamera, laserId):
    assert (laserId in LaserIdEnum.laserIdSet)
    return hndLib.cameraSetLaser(hndCamera, laserId)


def cameraGetNumLaser(hndCamera):
    return hndLib.cameraGetNumLaser(hndCamera)


def cameraSwitchToNextLaser(hndCamera):
    return hndLib.cameraSwitchToNextLaser(hndCamera)


def cameraGetNbProcessorRegNameAvailable(hndCamera):
    return hndLib.getNbProcessorRegNameAvailable(hndCamera)


def cameraProcessorRegNames(hndCamera):
    regNamesCount = cameraGetNbProcessorRegNameAvailable(hndCamera)
    regNamesList = []
    for i in range(0, regNamesCount):
        regName = hndLib.cameraGetRegisterName(hndCamera, i)
        regNamesList.append(regName)
    return regNamesList
