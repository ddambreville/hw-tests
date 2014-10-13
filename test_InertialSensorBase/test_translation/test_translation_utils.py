'''
Created on October 13, 2014

@author: amartin
'''

import time


def robot_motion(config_test, motion):
    """
    Move function
    """
    time_test = float(config_test.get('Test_Config', 'Test_time'))
    robot_velocity = float(config_test.get('Test_Config', 'Robot_velocity'))
    motion.move(robot_velocity, 0, 0)
    time.sleep(time_test)
    motion.stopMove()


def record_inertialbase_data(
        get_all_inertialbase_objects, thread):
    """
    Function which logs the inertial base datas
    """
    logger = get_all_inertialbase_objects["logger"]
    coord = ["X", "Y", "Z"]
    t_0 = time.time()
    while thread.isAlive():
        for each in coord:
            logger.log(("Acc" + each, get_all_inertialbase_objects[
                "Acc" + each].value))
            logger.log(("Angle" + each, get_all_inertialbase_objects[
                "Angle" + each].value))
            logger.log(("Gyr" + each, get_all_inertialbase_objects[
                "Gyr" + each].value))
        logger.log(("Time", time.time() - t_0))
        time.sleep(0.005)
    return logger
