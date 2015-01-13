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
    if message =='start':
        status = raw_input('start test ? (y/n)')
    else:
        status = raw_input('continue ' + message + '? (y/n)')


    if status =='y' or status=='yes':
        pass
    else:
        flag_obstacle=True


def stop_robot(list_wheel_speed):
    """
    Stop the robot
    """
    for speed in list_wheel_speed:
        speed.qvalue = (0.0, 0)

def move_robot(motion):

    
    parameters_rotation = tools.read_section("config.cfg", "Rotation")
    nb_tour = int(parameters_rotation['nb_tour'][0])
    nb_test = int(parameters_rotation['nb_test'][0])

    question_continue('start')
    for test in range(0, nb_test):
        motion.moveTo(0, 0, math.pi*10)
        question_continue('reverse')

        motion.moveTo(0, 0, -math.pi*10)
        test+=1
        question_continue('restart')
    motion.rest()
    
def test_multi_direction(dcm, mem, motion, expressiveness, wait_time, wait_time_bumpers, 
                     min_fraction, max_fraction, max_random, 
                     stop_robot, wake_up_pos, 
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
