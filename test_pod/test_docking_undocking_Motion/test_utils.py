'''
Created on October 17, 2014

@author: amartin
'''


import time
from math import atan, degrees
from tools import Queue


def init():
    """
    Global varibale "QUEUE" initialization
    """
    global QUEUE
    QUEUE = Queue()


def log_data(logger, get_pod_objects, coord):
    """
    Log data function
    """
    if coord[1] == 0:
        logger.log(("Angle", 0))
    else:
        logger.log(("Angle", degrees(atan(coord[0] / coord[1]))))
    logger.log(("robot_on_charging_station", get_pod_objects[
        "robot_on_charging_station"].value))
    logger.log(("backbumper", get_pod_objects[
        "backbumper"].value))
    logger.log(("battery_current", get_pod_objects[
        "battery_current"].value))
    QUEUE.enqueue("Arret")


def leave_station(alrecharge):
    """
    Robot leaves POD
    """
    print "leaveStation"
    result = alrecharge.leaveStation()
    print result
    if result == False:
        QUEUE.enqueue("Fail")
    else:
        QUEUE.enqueue("move")
    time.sleep(4)


def move(motion, coord):
    """
    Robot moves away from the POD
    """
    print "move"
    motion.moveTo(coord[0], coord[1], 0, 8)
    time.sleep(1)
    QUEUE.enqueue("lookForStation")


def look_for_station(alrecharge):
    """
    Robot looks for POD
    """
    print "lookForStation"
    tab = alrecharge.lookForStation()
    print tab
    if tab[0] == True:
        QUEUE.enqueue("moveInFrontOfStation")
    else:
        QUEUE.enqueue("Fail")
    time.sleep(1)


def move_front_station(alrecharge):
    """
    Robots moves in front the POD
    """
    print "moveInFrontOfStation"
    result = alrecharge.moveInFrontOfStation()
    print result
    if result == True:
        QUEUE.enqueue("dockOnStation")
    else:
        QUEUE.enqueue("Fail")
    time.sleep(1)


def dock_on_station(alrecharge):
    """
    Robot docks on the POD
    """
    print "dockOnStation"
    result = alrecharge.dockOnStation()
    print result
    if result == True:
        QUEUE.enqueue("log_data")
    else:
        QUEUE.enqueue("Fail")
    time.sleep(1)
