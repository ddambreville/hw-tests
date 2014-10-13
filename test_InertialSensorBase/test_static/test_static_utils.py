'''
Created on September 29, 2014

@author: amartin
'''

import time
from termcolor import colored

GRAVITY = 9.81

def wait(config_test):
    """
    Wait function
    """
    time_test = float(config_test.get('Test_Config', 'Test_time'))
    time.sleep(time_test)

def print_error(sensor, value, result):
    """
    printe the error messages on the console
    """
    result.append("Fail")
    print sensor + " : " + colored("Fail", "red")
    print sensor + " value = " + str(value)
    return result

def error(logger, sensor, tolerance, result):
    """
    Docstring
    """
    for index, each in enumerate(logger.log_dic[sensor]):
        if sensor == "AccZ":
            if abs((each - GRAVITY)/GRAVITY) > tolerance:
                result = print_error(sensor, each, result)
                break
            elif index == len(logger.log_dic[sensor]) - 1:
                print sensor + " : " + colored("Pass", "green")
        else:
            if abs(each) > tolerance:
                result = print_error(sensor, each, result)
                break
            elif index == len(logger.log_dic[sensor]) - 1:
                print sensor + " : " + colored("Pass", "green")
    return result

def check_error(logger, config_test):
    """
    check error function
    """
    tolerance_acc_xy = float(config_test.get('Test_Config', 'Tolerance_Acc_XY'))
    tolerance_acc_z = float(config_test.get('Test_Config', 'Tolerance_Acc_Z'))
    tolerance_angle_xy = float(config_test.get(
        'Test_Config', 'Tolerance_Angle_XY'))
    tolerance_gyr_all = float(config_test.get(
        'Test_Config', 'Tolerance_Gyr_All'))
    result = []
    coord = ["X", "Y"]
    for each in coord:
        result = error(logger, "Acc" + each, tolerance_acc_xy, result)
        result = error(logger, "Angle" + each, tolerance_angle_xy, result)
        result = error(logger, "Gyr" + each, tolerance_gyr_all, result)
    result = error(logger, "AccZ", tolerance_acc_z, result)
    result = error(logger, "GyrZ", tolerance_gyr_all, result)
    return result

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
