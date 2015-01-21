import pytest
import tools
import subdevice
import threading
import time
import sys
import math
import mobile_base_utils
from naoqi import ALProxy


def question_continue(message):
    """
    Ask user to write "y" or "yes" if he wants to continue and "n" otherwise
    """
    if message == 'start':
        status = raw_input('start test ? (y/n)')
    else:
        status = raw_input('continue ' + message + '? (y/n)')

    if status == 'y' or status == 'yes':
        pass
    else:
        flag_obstacle = True


def slope_detection(motion, stiffness, mem, wait):
    """
    Stop Movment when a slope is detected by robot
    """
    slope_detection = mem.getData('ALMotion/Safety/RobotOnASlope')
    while slope_detection == 'false':
        if slope_detection == 'true':
            motion.stopMove()
            if stiffness == 0:
                motion.rest()
                print 'Check position of the robot'
                time.sleep(wait)
                print 'Check position of the robot again'
                motion.wakeUp()
            else:
                print 'Check position of the robot'
                time.sleep(wait)
                print 'Check position of the robot again'
                pass


def stop_robot(list_wheel_speed):
    """
    Stop the robot
    """
    for speed in list_wheel_speed:
        speed.qvalue = (0.0, 0)


def move_robot(motion, mem):
    """
    Move Robot and stop when a fall id detected
    """
    parameters_slope = tools.read_section("config.cfg", "Stop_Slope")
    distance = float(parameters_slope["distance"][0])
    dir_x = int(parameters_slope["dir_X"][0])
    dir_y = int(parameters_slope["dir_Y"][0])
    dir_diag_l = int(parameters_slope["dir_diagL"][0])
    dir_diag_r = int(parameters_slope["dir_diagR"][0])
    stiffness = int(parameters_slope["stiff_ON"][0])
    wait = int(parameters_slope["wait_time"][0])

    question_continue('start')
    if dir_x == 1:
        question_continue('forward')
        motion.moveTo(distance, 0, 0)
        slope_detection(motion, stiffness, mem, wait)
        question_continue('behind')
        motion.moveTo(-distance, 0, 0)
        slope_detection(motion, stiffness, mem, wait)

    if dir_y == 1:
        question_continue('left')
        motion.moveTo(0, distance, 0)
        slope_detection(motion, stiffness, mem, wait)
        question_continue('rigth')
        motion.moveTo(0, -distance, 0)
        slope_detection(motion, stiffness, mem, wait)

    if dir_diag_l == 1:
        question_continue('diagonale front left')
        motion.moveTo(distance, distance, 0)
        slope_detection(motion, stiffness, mem, wait)
        question_continue('diagonale back left')
        motion.moveTo(-distance, -distance, 0)
        slope_detection(motion, stiffness, mem, wait)

    if dir_diag_r == 1:
        question_continue('diagonale front right')
        motion.moveTo(distance, -distance, 0)
        slope_detection(motion, stiffness, mem, wait)
        question_continue('diagonale back right')
        motion.moveTo(-distance, distance, 0)
        slope_detection(motion, stiffness, mem, wait)

    motion.rest()


def test_multi_direction(dcm, mem, motion, wait_time, stop_robot, wake_up_pos):

    motion.setExternalCollisionProtectionEnabled('All', False)
    motion.setDiagnosisEffectEnabled(False)

    try:
        motion.wakeUp()
        move_robot(motion, mem)

    except KeyboardInterrupt:
        motion.rest()
        print "\n******* User interrupt - ending test *******"
        pass
