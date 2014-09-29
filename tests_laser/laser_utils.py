#-*- coding: iso-8859-15 -*-

'''
Created on September 11, 2014

@author: amartin
'''


from termcolor import colored
import ConfigParser
import CameraViewer


def laser_error_code():
    """
    laser_error_code
    """
    error_code = ConfigParser.ConfigParser()
    error_code.read('CodeErrorLaser.cfg')
    return error_code


def get_nack_error(device, memory):
    """
    Get Nack & Error
    """
    ack = memory.getData("Device/DeviceList/" + device + "/Ack")
    nack = memory.getData("Device/DeviceList/" + device + "/Nack")
    error = memory.getData("Device/DeviceList/" + device + "/Error")
    return ack, nack, error


def ecriture(device, ack, nack, error, error_code):
    """
    Display
    """
    result = []
    print "******* " + device + " *******"
    if ack > 20:
        print "ACK : ", colored(str(ack), 'green')
    else:
        print "ACK : ", colored(str(ack), 'red')
        result.append("Fail")
    if nack < 20:
        print "NACK : ", colored(str(nack), 'green')
    else:
        print "NACK : ", colored(str(nack), 'red')
        result.append("Fail")
    if error == 0:
        print "Error : ", colored(str(error), 'green')
    else:
        print "Error : ", colored(str(error), 'red')
        result.append("Fail")
        print colored("Error name :", 'yellow'),
        colored(error_code.get(str(error), 'error'), 'yellow')
        print colored("Suggested fix :", 'yellow'),
        colored(error_code.get(str(error), 'fix'), 'yellow')
    return result


def check_front_laser(memory, error_code):
    """
    Front Laser
    """
    ack, nack, error = get_nack_error("LaserSensorFrontPlatform", memory)
    result = ecriture("Front Laser", ack, nack, error, error_code)
    return result


def check_right_laser(memory, error_code):
    """
    Right Laser
    """
    ack, nack, error = get_nack_error("LaserSensorRightPlatform", memory)
    result = ecriture("Right Laser", ack, nack, error, error_code)
    return result


def check_left_laser(memory, error_code):
    """
    Left Laser
    """
    ack, nack, error = get_nack_error("LaserSensorLeftPlatform", memory)
    result = ecriture("Left Laser", ack, nack, error, error_code)
    return result


def minimal_horizontal_x_distance(get_horizontal_x_segments):
    """
    Return the minimal X distance
    """
    dist_min = get_horizontal_x_segments["seg1"].value
    seg = 1
    for i in range(2, 16):
        if get_horizontal_x_segments["seg" + str(i)].value < dist_min:
            dist_min = get_horizontal_x_segments["seg" + str(i)].value
            seg = i
    return dist_min, seg


def save_laser_image(cam, path, thread):
    """
    Save laser images with cameraviewer
    """
    i = 0
    while thread.isAlive():
        CameraViewer.save_image(cam, path, str(i))
        i = i + 1
