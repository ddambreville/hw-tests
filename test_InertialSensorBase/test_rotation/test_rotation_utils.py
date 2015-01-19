'''
Created on October 02, 2014

@author: amartin

'''

import time


def robot_motion(motion, config_test):
    """
    Thread which make the robot move
    """
    rotation_speed = float(config_test.get('Test_Config', 'Rotation_speed'))
    time_test = float(config_test.get('Test_Config', 'Test_time'))
    motion.move(0, 0, rotation_speed)
    time.sleep(time_test)
    motion.stopMove()


def record_inertialbase_data(
        get_all_inertialbase_objects, thread, config_test):
    """
    Function which logs the datas
    """
    angle_tolerance = float(config_test.get('Test_Config', 'Angle_tolerance'))
    logger = get_all_inertialbase_objects["logger"]
    t_0 = time.time()
    while thread.isAlive():
        logger.log(("AngleZ", get_all_inertialbase_objects[
            "AngleZ"].value))
        logger.log(("GyrZ", get_all_inertialbase_objects[
            "GyrZ"].value))
        logger.log(("Tolerance_Angle_sup", angle_tolerance))
        logger.log(("Tolerance_Angle_inf", - angle_tolerance))
        logger.log(("Time", time.time() - t_0))
    return logger


def check_error(logger, config_test):
    """
    Function which checks the error
    at the end of the test
    """
    angle_tolerance = float(config_test.get('Test_Config', 'Angle_tolerance'))
    result = []
    for each in logger.log_dic["AngleZ"]:
        if abs(each) > angle_tolerance:
            result.append("Fail")
            print "Angle Z = " + str(each)
            break
    return result
