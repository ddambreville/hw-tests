'''
Created on August 22, 2014

@author: amartin

This script tests the X coordinates of the horizontal lasers.
Use the configuration file TestConfig.cfg to choose which
horizontal laser you want to test.

[Initial conditions]
The robot must be in front of a wall or a flat object.
Make a noaqi restart before the test to reset the odometry.
>>>>>>> df9f636... Update of horizontal X test scripts

'''

from qha_tools import switch, case
import threading
from termcolor import colored


def robot_motion(motion, pos_0, coord, side, config_test):
    """
    Thread which make the robot move
    according to the side to tested
    """
    distance = float(config_test.get('Test_Config', 'Distance_travel'))
    while abs(motion.getRobotPosition(True)[coord] - pos_0) < distance:
        print abs(motion.getRobotPosition(True)[coord] - pos_0)
        while switch(side):
            if case("Front"):
                motion.move(-0.1, 0, 0)
                break
            if case("Right"):
                motion.move(0, 0.1, 0)
                break
            if case("Left"):
                motion.move(0, -0.1, 0)
                break
    motion.stopMove()


def record_horizontaux_data(
        get_horizontal_x_segments, motion, side, pos_0, coord,
        thread, config_test):
    """
    Function which logs the laser distances
    """
    logger = get_horizontal_x_segments["logger"]
    debut = float(config_test.get('Test_Config', 'Distance_begin'))
    dist = abs(motion.getRobotPosition(True)[coord] - pos_0)
    offset_front = float(config_test.get('Test_Config', 'Offset_Front'))
    offset_side = float(config_test.get('Test_Config', 'Offset_Side'))
    while dist < debut:
        dist = abs(motion.getRobotPosition(True)[coord] - pos_0)
    while thread.isAlive():
        if side == "Front":
            logger.log(("robot_pos", abs(
                motion.getRobotPosition(True)[coord] - pos_0) + offset_front))
        else:
            logger.log(("robot_pos", abs(
                motion.getRobotPosition(True)[coord] - pos_0) + offset_side))
        for i in range(1, 16):
            logger.log(("seg" + str(i), get_horizontal_x_segments[
                "seg" + str(i)].value))
    for seg in range(1, 16):
        for i in range(0, len(logger.log_dic["robot_pos"])):
            logger.log(("ErreurSeg" + str(seg), (abs(
                logger.log_dic["robot_pos"][i] - logger.log_dic["seg" + str(
                    seg)][i]) / logger.log_dic["robot_pos"][i]) * 100))
    return logger


def print_error(logger, index, each, i):
    """
    print error message
    """
    print "Seg" + str(i) + " : " + colored("Fail", "red")
    print "Position : " + str(logger.log_dic["robot_pos"][index])
    print "Erreur : " + str(each) + "%"


def check_error(logger, config_test):
    """
    Function which checks the distance error
    at the end of the test
    """
    result = []
    for i in range(1, 16):
        for index, each in enumerate(logger.log_dic["ErreurSeg" + str(i)]):
            tolerance = float(
                config_test.get('Horizontal_Tolerance', 'seg' + str(i)))
            if each > tolerance and logger.log_dic["robot_pos"][index] < 1:
                result.append('Fail')
                print_error(logger, index, each, i)
                break
            elif each > tolerance and logger.log_dic["seg" + str(i)][index] < 6:
                result.append('Fail')
                print_error(logger, index, each, i)
                break
            elif index == len(logger.log_dic["ErreurSeg" + str(i)]) - 1:
                result.append('Pass')
                print "Seg" + str(i) + " : " + colored("Pass", "green")
    return result


def test_horizontaux_x(
    check_error_laser, dcm, mem, motion, wakeup, side,
        get_horizontal_x_segments, config_test, remove_safety, remove_diagnosis):
    """
    Test main function which tests the X distance
    of the horizontal lasers
    """
    if side == "Front":
        pos_0 = motion.getRobotPosition(True)[0]
        coord = 0
    else:
        pos_0 = motion.getRobotPosition(True)[1]
        coord = 1
    motion_thread = threading.Thread(target=robot_motion, args=(
        motion, pos_0, coord, side, config_test))
    motion_thread.start()
    logger = record_horizontaux_data(
        get_horizontal_x_segments, motion, side, pos_0, coord, motion_thread,
        config_test)
    result = check_error(logger, config_test)
    assert 'Fail' not in result
