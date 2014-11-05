'''
Created on October 17, 2014

@author: amartin
'''


import time
from math import atan, degrees
from qha_tools import Queue


def init():
    """
    Global varibale "QUEUE" initialization
    """
    global QUEUE
    QUEUE = Queue()


def log_data(get_pod_objects, coord, log_file):
    """
    Log data function
    """
    print "log data"
    if coord[1] == 0:
        log_file.write(str(0) + ",")
    else:
        log_file.write(str(degrees(atan(coord[0] / coord[1]))) + ",")
    log_file.write(str(get_pod_objects[
        "robot_on_charging_station"].value) + ",")
    log_file.write(str(get_pod_objects[
        "backbumper"].value) + ",")
    log_file.write(str(get_pod_objects[
        "battery_current"].value) + "\n")
    log_file.flush()
    if get_pod_objects["robot_on_charging_station"].value == 1:
        QUEUE.enqueue("Arret")
    else:
        QUEUE.enqueue("Fail")


def leave_station(alrecharge, my_dict):
    """
    Robot leaves POD
    """
    print "leaveStation"
    result = alrecharge.leaveStation()
    print result
    my_dict["leaveStation"].append(result)
    if result == False:
        QUEUE.enqueue("leave_motion")
    else:
        QUEUE.enqueue("move")
    time.sleep(2)


def leave_motion(motion):
    """
    Robot leaves POD
    """
    print "leave_motion"
    motion.moveTo(0.5, 0, 0)
    QUEUE.enqueue("move")


def move(motion, coord):
    """
    Robot moves away from the POD
    """
    print "move"
    motion.moveTo(coord[0], coord[1], 0, 5)
    time.sleep(1)
    QUEUE.enqueue("lookForStation")


def look_for_station(alrecharge, my_dict):
    """
    Robot looks for POD
    """
    print "lookForStation"
    tab = alrecharge.lookForStation()
    print tab[0]
    my_dict["lookForStation"].append(tab[0])
    if tab[0] == True:
        QUEUE.enqueue("moveInFrontOfStation")
    else:
        QUEUE.enqueue("lookForStation")
    time.sleep(1)
    return tab[0]


def move_front_station(alrecharge, my_dict):
    """
    Robots moves in front the POD
    """
    print "moveInFrontOfStation"
    result = alrecharge.moveInFrontOfStation()
    print result
    my_dict["moveInFrontOfStation"].append(result)
    if result == True:
        QUEUE.enqueue("dockOnStation")
    else:
        QUEUE.enqueue("moveInFrontOfStation")
    time.sleep(1)
    return result


def dock_on_station(alrecharge, get_pod_objects, my_dict):
    """
    Robot docks on the POD
    """
    print "dockOnStation"
    result = alrecharge.dockOnStation()
    print result
    my_dict["dockOnStation"].append(result)
    time.sleep(7)
    if result == True or get_pod_objects[
            "robot_on_charging_station"].value == 1:
        QUEUE.enqueue("log_data")
    else:
        QUEUE.enqueue("dockOnStation")
    return result
