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
    Question
    """
    if message == 'start':
        status = raw_input('start test ? (y/n)')
    else:
        status = raw_input('continue ' + message + '? (y/n)')

    if status == 'y' or status == 'yes':
        pass
    else:
        flag_obstacle = True


def slope_detection(motion, stiffness, mem):

    slope_detection = mem.getData('ALMotion/Safety/RobotOnASlope')
    while slope_detection == 'false':
        if slope_detection == 'true':
            motion.stopMove()
            if stiffness == 0:
                motion.rest()
                print 'Check position of the robot'
                time.sleep(30)
                print 'Check position of the robot again'
                motion.wakeUp()
            else:
                print 'Check position of the robot'
                time.sleep(30)
                print 'Check position of the robot again'
                pass


def stop_robot(list_wheel_speed):
    """
    Stop the robot
    """
    for speed in list_wheel_speed:
        speed.qvalue = (0.0, 0)


def move_robot(motion, mem):

    parameters_slope = tools.read_section("config.cfg", "Stop_Slope")
    distance = float(parameters_slope["direction"][0])
    dir_X = int(parameters_slope["dir_X"][0])
    dir_Y = int(parameters_slope["dir_Y"][0])
    dir_diagL = int(parameters_slope["dir_diagL"][0])
    dir_diagR = int(parameters_slope["dir_diagR"][0])
    stiffness = int(parameters_slope["stiff_ON"][0])

    question_continue('start')
    if dir_X == 1:
        question_continue('forward')
        motion.moveTo(distance, 0, 0)
        slope_detection(motion, stiffness, mem)
        question_continue('behind')
        motion.moveTo(-distance, 0, 0)
        slope_detection(motion, stiffness, mem)
        
    if dir_Y == 1:
        question_continue('left')
        motion.moveTo(0, distance, 0)
        slope_detection(motion, stiffness, mem)
        question_continue('rigth')
        motion.moveTo(0, -distance, 0)
        slope_detection(motion, stiffness, mem)

    if dir_diagL == 1:
        question_continue('diagonale')
        motion.moveTo(distance, distance, 0)
        slope_detection(motion, stiffness, mem)
        question_continue('diagonale')
        motion.moveTo(-distance, -distance, 0)
        slope_detection(motion, stiffness, mem)

    if dir_diagR == 1:
        question_continue('diagonale')
        motion.moveTo(distance, -distance, 0)
        slope_detection(motion, stiffness, mem)
        question_continue('diagonale')
        motion.moveTo(-distance, distance, 0)
        slope_detection(motion, stiffness, mem)

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
