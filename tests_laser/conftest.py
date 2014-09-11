#-*- coding: iso-8859-15 -*-

'''
Created on September 11, 2014

@author: amartin
'''

from termcolor import colored
import ConfigParser
import pytest


def initialisation():
    """
    Initialisation
    """
    cfg = ConfigParser.ConfigParser()
    cfg.read('CodeErrorLaser.cfg')
    print "\n"
    return cfg


def get_nack_error(device, memory):
    """
    Get Nack & Error
    """
    ack = memory.getData("Device/DeviceList/" + device + "/Ack")
    nack = memory.getData("Device/DeviceList/" + device + "/Nack")
    error = memory.getData("Device/DeviceList/" + device + "/Error")
    return ack, nack, error


def ecriture(device, ack, nack, error, cfg):
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
        if (device == "Front Laser") or (device == "Right Laser")\
            or (device == "Left Laser"):
            print colored("Error name :", 'yellow'),
            colored(cfg.get(str(error), 'error'), 'yellow')
            print colored("Suggested fix :", 'yellow'),
            colored(cfg.get(str(error), 'fix'), 'yellow')
    return result


def check_front_laser(memory, cfg):
    """
    Front Laser
    """
    ack, nack, error = get_nack_error("LaserSensorFrontPlatform", memory)
    result = ecriture("Front Laser", ack, nack, error, cfg)
    return result


def check_right_laser(memory, cfg):
    """
    Right Laser
    """
    ack, nack, error = get_nack_error("LaserSensorRightPlatform", memory)
    result = ecriture("Right Laser", ack, nack, error, cfg)
    return result


def check_left_laser(memory, cfg):
    """
    Left Laser
    """
    ack, nack, error = get_nack_error("LaserSensorLeftPlatform", memory)
    result = ecriture("Left Laser", ack, nack, error, cfg)
    return result


@pytest.fixture(scope="module")
def check_error_laser(mem):
    """
    test - MAIN
    """
    cfg = initialisation()
    result_f = check_front_laser(mem, cfg)
    result_r = check_right_laser(mem, cfg)
    result_l = check_left_laser(mem, cfg)
    global_result = result_f + result_r + result_l
    assert 'Fail' not in global_result

    print "\n"
