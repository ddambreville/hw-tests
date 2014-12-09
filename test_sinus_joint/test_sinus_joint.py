# -*- coding: utf-8 -*-

'''
Created on November 27, 2014

@author: amartin
'''

import time
from subdevice import JointPositionActuator, WheelSpeedActuator
import threading


def log_joints(thread, bag_log, logger, time_test):
    '''
    Docstring
    '''
    time.sleep(2)
    while thread.isAlive():
        time.sleep(0.05)
    time_begin = time.time()
    delta_time = 0.0
    while delta_time < time_test:
        joints_value = bag_log.value
        delta_time = time.time() - time_begin
        logger.log(("Time", delta_time))
        for each in joints_value.keys():
            logger.log((each, joints_value[each]))
        time.sleep(0.01)


def thread_joints(list_points, obj):
    '''
    Docstring
    '''
    obj.mqvalue = list_points


def test_sinus_joint(period, kill_motion, stiff_joints,
                     bag_log, logger, points, dcm, mem, init_joint_position):
    '''
    Docstring
    '''
    time_test = float(period[0]) * int(period[1]) + float(period[0] / 4) + 3
    thread_list = []
    print "frequence = " + str(1 / period[0]) + "Hz"
    for each in points.keys():
        if "Wheel" in each:
            obj = WheelSpeedActuator(dcm, mem, each)
        else:
            obj = JointPositionActuator(dcm, mem, each)
        thread_list.append(threading.Thread(target=thread_joints, args=(
            points[each], obj)))
    for each in thread_list:
        each.start()
    log_joints(thread_list[0], bag_log, logger, time_test)
