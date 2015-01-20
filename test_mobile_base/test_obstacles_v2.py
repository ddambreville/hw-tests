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


def stop_robot(list_wheel_speed):
    """
    Stop the robot
    """
    for speed in list_wheel_speed:
        speed.qvalue = (0.0, 0)


def move_robot(motion):

    parameters_direction = tools.read_section("config.cfg", "Obstacle")
    distance = float(parameters_direction["direction"][0])
    nb_passage = int(parameters_direction["nb_passage"][0])
    dir_X = int(parameters_direction["dir_X"][0])
    dir_Y = int(parameters_direction["dir_Y"][0])
    dir_diagL = int(parameters_direction["dir_diagL"][0])
    dir_diagR = int(parameters_direction["dir_diagR"][0])
    rotate = int(parameters_direction["rotate"][0])

    question_continue('start')
    if rotate == 1:
        print 'rotate'
        motion.moveTo(0, 0, math.pi * 2)
    if dir_X == 1:
        question_continue('forward')
        motion.moveTo(distance, 0, 0)
        question_continue('behind')
        motion.moveTo(-distance, 0, 0)

    if dir_Y == 1:
        question_continue('left')
        motion.moveTo(0, distance, 0)
        question_continue('rigth')
        motion.moveTo(0, -distance, 0)

    if dir_diagL == 1:
        question_continue('diagonale front left')
        motion.moveTo(distance, distance, 0)
        question_continue('diagonale back left')
        motion.moveTo(-distance, -distance, 0)

    if dir_diagR == 1:
        question_continue('diagonale front right')
        motion.moveTo(distance, -distance, 0)
        question_continue('diagonale back right')
        motion.moveTo(-distance, distance, 0)

    motion.rest()


def test_multi_direction(dcm, mem, motion, expressiveness, wait_time,
                         wait_time_bumpers, min_fraction, max_fraction,
                         max_random, stop_robot, wake_up_pos,
                         stiff_robot_wheels,
                         log_wheels_speed):

    motion.setExternalCollisionProtectionEnabled('All', False)
    motion.setDiagnosisEffectEnabled(False)

    try:
        motion.wakeUp()
        move_robot(motion)

    except KeyboardInterrupt:
        motion.rest()
        print "\n******* User interrupt - ending test *******"
        pass
