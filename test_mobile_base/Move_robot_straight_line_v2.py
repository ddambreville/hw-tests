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

    Move_x = 0
    Move_y = 0
    diag_1 = 0
    diag_2 = 0
    parameters_direction = tools.read_section("config.cfg",
                                              "DirectionParameters")
    distance = int(parameters_direction["direction"][0])
    nb_passage = int(parameters_direction["nb_passage"][0])
    dir_X = int(parameters_direction["dir_X"][0])
    dir_Y = int(parameters_direction["dir_Y"][0])
    dir_diagL = int(parameters_direction["dir_diagL"][0])
    dir_diagR = int(parameters_direction["dir_diagR"][0])

    question_continue('start')
    if dir_X == 1:
        print 'move to X'
        for move_x in range(nb_passage):
            question_continue('forward')
            motion.moveTo(distance, 0, 0)
            question_continue('reverse')
            motion.moveTo(-distance, 0, 0)
            if move_x == nb_passage:
                move_x = 0
                question_continue('')
                pass

    if dir_Y == 1:
        question_continue('to Y')
        print 'move to Y'
        for move_y in range(nb_passage):
            question_continue('left')
            motion.moveTo(0, distance, 0)
            question_continue('right')
            motion.moveTo(0, -distance, 0)
            Move_y = +1
            if move_y == nb_passage:
                move_y = 0
                pass

    if dir_diagL == 1:
        question_continue('to diagonale')
        print 'move to first diagonale'
        for diag_1 in range(nb_passage):
            question_continue('diagonale front left')
            motion.moveTo(distance, distance, 0)
            question_continue('diagonale back left')
            motion.moveTo(-distance, -distance, 0)
            diag_1 = +1
            if diag_1 == nb_passage:
                diag_1 = 0
                pass

    if dir_diagR == 1:
        question_continue('to diagonale')
        print 'move to second diagonale'
        for diag_2 in range(nb_passage):
            question_continue('diagonale front right')
            motion.moveTo(distance, -distance, 0)
            question_continue('diagonale back right')
            motion.moveTo(-distance, distance, 0)
            diag_2 = +1
            if diag_2 == nb_passage:
                diag_2 = 0
                pass

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
