import pytest
import tools
import subdevice
import threading
import time
import sys
import math
import random
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

    parameters_direction = tools.read_section("config.cfg", "DirectionParameters")
    distance = int(parameters_direction["direction"][0])
    parameters_speed = tools.read_section("config.cfg", "Speed")
    min = int(parameters_speed["min_speed"][0])
    nom = int(parameters_speed["nom_speed"][0])
    max = int(parameters_speed["max_speed"][0])

    question_continue('start')
    if min==1:
    	print 'minimal velocity'
    	motion.moveToward(0.05, 0.0, 0.0)
    	time.sleep(6.0)
    	motion.stopMove()


    if nom==1:
    	question_continue('nominal velocity')
    	print 'nomimal velocity'
    	motion.moveToward(0.3, 0.0, 0.0)
    	time.sleep(6.0)
    	motion.stopMove()

    if max==1:
    	question_continue('maximal velocity')
    	print 'maximal velocity'
    	motion.moveToward(1.0, 0.0, 0.0)
    	time.sleep(5.0)
    	motion.stopMove()

    motion.rest()


def test_move_random(motion, dcm, mem, leds, expressiveness, wait_time, wait_time_bumpers,
                 min_fraction, max_fraction, max_random,
                 stop_robot, wake_up_pos,
                 stiff_robot_wheels, unstiff_joints,
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
