'''
Created on August 22, 2014

@author: amartin
'''

import threading
import time
from termcolor import colored


def dance_motion(dance, behavior_manager):
    """
    Dance motion
    """
    apps_list = behavior_manager.getBehaviorNames()
    # print apps_list
    dance = "User/" + dance
    if dance in apps_list:
        behavior_manager.startBehavior(dance)
        while behavior_manager.isBehaviorRunning(dance):
            print "hihi"
            time.sleep(0.5)


def test_faux_positifs_dance(mem, remove_diagnosis, wakeup, dance,
                             remove_safety, behavior_manager):
            time.sleep(0.5)


def record_laser_data(lasers_dico, thread):
    """
    Record laser data
    """
    logger = lasers_dico["logger_dist"]
    h_sides = ["Front", "Left", "Right"]
    v_sides = ["Left", "Right"]
    while thread.isAlive():
        for each in h_sides:
            for i in range(1, 16):
                logger.log(("Horizontal_X_seg" + str(i) + "_" +
                            each, lasers_dico["Horizontal_X_seg" + str(i) +
                                              "_" + each].value))
        for each in v_sides:
            logger.log(
                ("Vertical_X_seg01_" + each, lasers_dico["Vertical_X_seg01_" +
                                                         each].value))
        for i in range(1, 4):
            logger.log(
                ("Shovel_X_seg" + str(i), lasers_dico["Shovel_X_seg" +
                                                      str(i)].value))
    return logger


def check_error(lasers_dico, logger_d, config_test):
    """
    Check the test result
    """
    result = []
    logger_e = lasers_dico["logger_error"]
    h_sides = ["Front", "Left", "Right"]
    v_sides = ["Left", "Right"]
    h_distance = float(config_test.get('Distance_Max', 'Horizontal'))
    v_distance = float(config_test.get('Distance_Max', 'Vertical'))
    s_distance = float(config_test.get('Distance_Max', 'Shovel'))
    for side in h_sides:
        for i in range(1, 16):
            for each in logger_d.log_dic["Horizontal_X_seg" + str(i) +
                                         "_" + side]:
                if each < h_distance:
                    result.append('Fail')
                    logger_e.log(
                        ("Horizontal_X_seg" + str(i) + "_" + side, each))
                else:

                    pass

    for side in v_sides:
        for each in logger_d.log_dic["Vertical_X_seg01_" + side]:
            if each < v_distance:
                result.append('Fail')
                logger_e.log(
                    ("Vertical_X_seg01_" + side, each))
            else:
                pass

    for i in range(1, 4):
        for each in logger_d.log_dic["Shovel_X_seg" + str(i)]:
            if each < s_distance:
                result.append('Fail')
                logger_e.log(
                    ("Shovel_X_seg" + str(i), each))
            else:
                pass
    return result, logger_e


def test_faux_positifs_dance(mem, dcm, remove_diagnosis, wakeup, dance,
                             remove_safety, behavior_manager, active_all_laser,
                             get_lasers_x_segments, config_test):
    """
    Test function
    """
    dance_thread = threading.Thread(
        target=dance_motion, args=(dance, behavior_manager))
    dance_thread.start()
    print "Initialisation..."
    time.sleep(5)
    print "Test..."
    logger_d = record_laser_data(get_lasers_x_segments, dance_thread)
    result, logger_e = check_error(
        get_lasers_x_segments, logger_d, config_test)
    if 'Fail' in result:
        print "NUMBER OF POSITIVES FALSE PER SEGMENT"
        for each in logger_e.log_dic.keys():
            print each + ":" + str(len(logger_e.log_dic[each]))
    assert 'Fail' not in result
