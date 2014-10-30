'''
Created on August 22, 2014

@author: amartin

[Description]
This script tests there aren't positives false on
the lasers (horizontal, vertical & shovel) during a dance.

[Initial conditions]
Place the robot in a free area, without anything around him.
Check that the dance(s) in the config file (TestConfig.cfg)
is(are) correctly installed.
'''

import threading
import time

H_SIDES = ["Front", "Left", "Right"]
V_SIDES = ["Left", "Right"]
S_SIDES = ["Front", "Back"]


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
            time.sleep(0.5)


def record_sensor_data(lasers_dico, thread):
    """
    Record laser data
    """
    logger = lasers_dico["logger_dist"]
    bag = lasers_dico["bag"]
    time_debut = time.time()
    while thread.isAlive():
        joints_value = bag.value
        for each in joints_value.keys():
            logger.log((each, joints_value[each]))
        logger.log(("Time", time.time() - time_debut))
    return logger


def check_error(lasers_dico, logger_d, config_test):
    """
    Check the test result
    """
    result = []
    logger_e = lasers_dico["logger_error"]

    h_distance = float(config_test.get('Distance_Min', 'Horizontal'))
    v_distance = float(config_test.get('Distance_Min', 'Vertical'))
    s_distance = float(config_test.get('Distance_Min', 'Shovel'))
    so_distance = float(config_test.get('Distance_Min', 'Sonar'))
    for side in H_SIDES:
        for i in range(1, 16):
            for each in logger_d.log_dic["Horizontal_X_seg" + str(i) +
                                         "_" + side]:
                if each < h_distance:
                    result.append('Fail')
                    logger_e.log(
                        ("Horizontal_X_seg" + str(i) + "_" + side, each))
                else:

                    pass

    for side in V_SIDES:
        for each in logger_d.log_dic["Vertical_X_seg01_" + side]:
            if each < v_distance:
                result.append('Fail')
                logger_e.log(
                    ("Vertical_X_seg01_" + side, each))
    for side in S_SIDES:
        for each in logger_d.log_dic["Sonar_" + side]:
            if each < so_distance:
                result.append('Fail')
                logger_e.log(
                    ("Sonar_" + side, each))
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


def test_faux_positifs_dance(
    check_error_laser, mem, dcm, remove_diagnosis, wakeup, dance,
    remove_safety, behavior_manager, active_all_laser,
        get_sensor_objects, config_test):
    """
    Test function
    """
    dance_thread = threading.Thread(
        target=dance_motion, args=(dance, behavior_manager))
    dance_thread.start()
    print "Initialisation..."
    time.sleep(5)
    print "Test..."
    logger_d = record_sensor_data(get_sensor_objects, dance_thread)
    result, logger_e = check_error(
        get_sensor_objects, logger_d, config_test)
    if 'Fail' in result:
        print "NUMBER OF POSITIVES FALSE PER SEGMENT"
        for each in logger_e.log_dic.keys():
            print each + ":" + str(len(logger_e.log_dic[each]))
    assert 'Fail' not in result
