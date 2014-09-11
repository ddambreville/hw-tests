'''
Created on September 5, 2014

@author: amartin

[Description]
This script tests the X coordinates of the vertical lasers.

[Initial conditions]
The robot must be in front of a wall or a flat object.
Make a noaqi restart before the test to reset the odometry.

'''
import threading
from termcolor import colored


def robot_motion(motion, pos_0, config_test):
    """
    Thread which make the robot move
    according to the side to tested
    """
    distance = float(config_test.get('Test_Config', 'Distance_travel'))
    while abs(motion.getRobotPosition(True)[0] - pos_0) < distance:
        print abs(motion.getRobotPosition(True)[0] - pos_0)
        motion.move(-0.1, 0, 0)
    motion.stopMove()


def record_vertical_data(
        get_vertical_x_segments, motion, pos_0,
        thread, config_test):
    """
    Function which logs the laser distances
    """
    logger = get_vertical_x_segments["logger"]
    debut = float(config_test.get('Test_Config', 'Distance_begin'))
    dist = abs(motion.getRobotPosition(True)[0] - pos_0)
    offset_front = float(config_test.get('Test_Config', 'Offset_Front'))
    while dist < debut:
        dist = abs(motion.getRobotPosition(True)[0] - pos_0)
    while thread.isAlive():

        logger.log(("robot_pos", abs(
            motion.getRobotPosition(True)[0] - pos_0) + offset_front))
        logger.log(("Verti_Right", get_vertical_x_segments[
            "Verti_Right"].value))
        logger.log(("Verti_Left", get_vertical_x_segments[
            "Verti_Left"].value))
    for i in range(0, len(logger.log_dic["robot_pos"])):
        logger.log(("Erreur_Verti_Right", (abs(
            logger.log_dic["robot_pos"][i] - logger.log_dic[
                "Verti_Right"][i]) / logger.log_dic["robot_pos"][i]) * 100))
        logger.log(("Erreur_Verti_Left", (abs(
            logger.log_dic["robot_pos"][i] - logger.log_dic[
                "Verti_Left"][i]) / logger.log_dic["robot_pos"][i]) * 100))
    return logger


def print_error(logger, name, error_vl, i):
    """
    Print error message
    """
    print name + " : " + colored("Fail", "red")
    print "Position : " + str(logger.log_dic["robot_pos"][i])
    print "Erreur : " + str(error_vl) + "%"


def check_error(logger, config_test):
    """
    Function which checks the distance error
    at the end of the test
    """
    side = ["Left", "Right"]
    result = []
    tolerance = float(
        config_test.get('Test_Config', "Tolerance"))
    print len(logger.log_dic["robot_pos"])
    for each in side:
        for i in range(0, len(logger.log_dic["robot_pos"]) - 1):
            error_vl = logger.log_dic["Erreur_Verti_" + each][i]
            if error_vl > tolerance:
                result.append('Fail')
                print_error(logger, "Verti_" + each, error_vl, i)
                break
            elif i == len(logger.log_dic["robot_pos"]) - 2:
                result.append('Pass')
                print "Verti" + each + " : " + colored("Pass", "green")

    return result


def test_verticaux_x(
    check_error_laser, dcm, mem, motion, wakeup, get_vertical_x_segments,
        config_test, remove_safety, remove_diagnosis):
    """
    Test main function which tests the X distance
    of the horizontal lasers
    """
    pos_0 = motion.getRobotPosition(True)[0]
    motion_thread = threading.Thread(target=robot_motion, args=(
        motion, pos_0, config_test))
    motion_thread.start()
    logger = record_vertical_data(
        get_vertical_x_segments, motion, pos_0, motion_thread,
        config_test)
    result = check_error(logger, config_test)
    assert 'Fail' not in result
