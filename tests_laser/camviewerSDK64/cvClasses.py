'''
Version : 1
File    : cvClasses.py
Created : 24.06.2014
Author  : Ahmed Lazreg
          (c) 2014 Aldebaran Robotics. All rights reserved.

Description: Python binding to CameraViewer internals
    "Camera" class implements all methods exported by the binding module

Requirement: Python 2.7.3
'''

from pybinding import *


class Camera(object):

    def __init__(self, boardLoc):
        assert (boardLoc in BoardLocationEnum.boardLocationSet)
        self.obj = cameraCreate(boardLoc)

    def __del__(self):
        self.disconnect()
        cameraDestroy(self.obj)
        pass

    def connect(self):
        return cameraConnect(self.obj)

    def disconnect(self):
        cameraDisconnect(self.obj)

    def isConnected(self):
        return cameraIsConnected(self.obj)

    def getBoardLocation(self):
        return cameraGetBoardLocation(self.obj)

    def getImage(self):
        return cameraGetImage(self.obj)

    '''
    @options: OR'ed options from ImageSaveOptionsEnum
    @return
        RESULT_OK                       = 1
        RESULT_ERR_IMAGE_EMPTY          = 2;
        RESULT_ERR_SAVING_IMAGE_FILE    = 3;
        RESULT_ERR_INVALID_SCALE_FACTOR = 4;
    note: the image format is inferred from filename extension. It's better to choose BMP because it's lossless format.
          Generated images are ARGB format.
    '''

    def saveImageToFile(self, fileName, options=ImageSaveOptionsEnum.kOpt_OverlayOn, imageScaleFactor=3):
        return cameraSaveImageToFile(self.obj, fileName, options, imageScaleFactor)

    def getFrameNumber(self):
        return cameraGetFrameNumber(self.obj)

    def getProcessorRegister(self, regIndex):
        return cameraGetProcessorRegister(self.obj, regIndex)

    def getProcessorRegisterByName(self, regName):
        return cameraGetProcessorRegisterByName(self.obj, regName)

    def getIntegrationTime(self):
        return cameraGetIntegrationTime(self.obj)

    def setLaser(self, laserId):
        return cameraSetLaser(self.obj, laserId)

    def getNumLaser(self):
        return cameraGetNumLaser(self.obj)

    def switchToNextLaser(self):
        return cameraSwitchToNextLaser(self.obj)

    def getProcessorRegNamesList(self):
        return cameraProcessorRegNames(self.obj)
