'''
Created on September 25, 2014

@author: amartin

[Description]
This script tests the distances returned by the front or the back sonar.

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
    sonar = config_test.get('Test_Config', 'Sonar')
    while abs(motion.getRobotPosition(True)[0] - pos_0) < distance:
        print abs(motion.getRobotPosition(True)[0] - pos_0)
        if sonar == "Front":
            motion.move(-0.1, 0, 0)
        elif sonar == "Back":
            motion.move(0.1, 0, 0)
        else:
            print "error : sonar must be 'Back' or 'Front'"
            break
    motion.stopMove()


def record_sonar_data(
        get_sonar_objects, motion, pos_0,
        thread, config_test):
    """
    Function which logs the sonar distances
    """
    sonar = config_test.get('Test_Config', 'Sonar')
    logger = get_sonar_objects["logger"]
    debut = float(config_test.get('Test_Config', 'Distance_begin'))
    dist = abs(motion.getRobotPosition(True)[0] - pos_0)
    offset_front = float(config_test.get('Test_Config', 'Offset_Front'))
    while dist < debut:
        dist = abs(motion.getRobotPosition(True)[0] - pos_0)
    while thread.isAlive():
        logger.log(("robot_pos", abs(
            motion.getRobotPosition(True)[0] - pos_0) + offset_front))
        logger.log((sonar + "_Sonar", get_sonar_objects[
            sonar + "_Sonar"].value))
    for i in range(0, len(logger.log_dic["robot_pos"])):
        logger.log(("Erreur_" + sonar + "_Sonar", (abs(
            logger.log_dic["robot_pos"][i] - logger.log_dic[
                sonar + "_Sonar"][i]) / logger.log_dic["robot_pos"][i]) * 100))
    return logger


def print_error(logger, name, error_v, i):
    """
    Print error message
    """
    print name + " : " + colored("Fail", "red")
    print "Position : " + str(logger.log_dic["robot_pos"][i])
    print "Erreur : " + str(error_v) + "%"


def check_error(logger, config_test):
    """
    Function which checks the distance error
    at the end of the test
    """
    result = []
    sonar = config_test.get('Test_Config', 'Sonar')
    tolerance = float(
        config_test.get('Test_Config', "Tolerance"))
    for i in range(0, len(logger.log_dic["robot_pos"]) - 1):
        error = logger.log_dic[sonar + "_Sonar"][i]
        if error > tolerance:
            result.append('Fail')
            print_error(logger, sonar + "_Sonar", error, i)
            break
        elif i == len(logger.log_dic["robot_pos"]) - 2:
            result.append('Pass')
            print sonar + "_Sonar : " + colored("Pass", "green")
    return result


def test_verticaux_x(
    dcm, mem, motion, wakeup_no_rotation, get_sonar_objects,
        config_test, remove_safety, remove_diagnosis):
    """
    Test main function which tests the X distance
    of the horizontal lasers
    """
    pos_0 = motion.getRobotPosition(True)[0]
    motion_thread = threading.Thread(target=robot_motion, args=(
        motion, pos_0, config_test))
    motion_thread.start()
    logger = record_sonar_data(
        get_sonar_objects, motion, pos_0, motion_thread,
        config_test)
    result = check_error(logger, config_test)
    assert 'Fail' not in result
