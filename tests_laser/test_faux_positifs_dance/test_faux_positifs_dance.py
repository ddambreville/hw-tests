'''
Created on August 22, 2014

@author: amartin
'''

import threading
import time


def dance_motion(dance, behavior_manager):
    """
    Dance function
    """
    apps_list = behavior_manager.getBehaviorNames()
    # print apps_list
    dance = "User/" + dance
    if dance in apps_list:
        print "haha"
        behavior_manager.startBehavior(dance)
        while behavior_manager.isBehaviorRunning(dance):
            print "hihi"
            time.sleep(0.5)


def test_faux_positifs_dance(mem, remove_diagnosis, wakeup, dance,
                             remove_safety, behavior_manager):
            time.sleep(0.5)


def record_laser_data(lasers_dico, thread):
    logger = get_horizontal_x_segments["logger"]
    h_sides = ["Front", "Left", "Right"]
    v_sides = ["Left", "Right"]
    while thread.isAlive():
        for each in h_sides:
            for i in range(1, 10):
                logger.log(("Horizontal_X_seg" + str(i) + "_" +
                            each, lasers_dico["Horizontal_X_seg" + str(i) +
                                              "_" + each].value))
            for i in range(10, 16):
                logger.log(
                    ("Horizontal_X_seg" + str(i) + "_" +
                     each, lasers_dico["Horizontal_X_seg" + str(i) +
                                       "_" + each].value))
        for each in v_sides:
            logger.log(
                ("Vertical_X_seg01_" + each, lasers_dico["Vertical_X_seg01_" + each].value))
        for i in range(1, 4):
            logger.log(
                ("Shovel_X_seg" + str(i) + each, lasers_dico["Shovel_X_seg" + str(i)].value))

    return logger


def test_faux_positifs_dance(mem, remove_diagnosis, wakeup, dance,
                             remove_safety, behavior_manager, get_lasers_x_segments):
    """
    Test function
    """
    print dance
    time.sleep(10)
    #dance_thread = threading.Thread(target=dance_motion, args=(dance, behavior_manager))
    # dance_thread.start()
    dance_motion(dance, behavior_manager)

    time.sleep(2)
    dance_thread = threading.Thread(
        target=dance_motion, args=(dance, behavior_manager))
    dance_thread.start()
    time.sleep(10)
    logger = record_laser_data(get_lasers_x_segments, dance_thread)
    print logger.log_dic
