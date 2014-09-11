#-*- coding: iso-8859-15 -*-

'''
Created on September 11, 2014

@author: amartin
'''


import pytest
from subdevice import Laser
import tools
import laser_utils


@pytest.fixture(scope="module")
def check_error_laser(mem):
    """
    test - MAIN
    """
    cfg = laser_utils.laser_error_code()
    result_f = laser_utils.check_front_laser(mem, cfg)
    result_r = laser_utils.check_right_laser(mem, cfg)
    result_l = laser_utils.check_left_laser(mem, cfg)
    global_result = result_f + result_r + result_l
    assert 'Fail' not in global_result
    print "\n"


@pytest.fixture(scope="module")
def get_vertical_x_segments(request, result_base_folder, dcm, mem):
    """
    Return a dictionary with several objects for
    each X coordinate of all horizontal segments
    """
    dico = {}
    dico["Verti_Right"] = Laser(
        dcm, mem, "Front/Vertical/Right/Seg01/X/Sensor")
    dico["Verti_Left"] = Laser(
        dcm, mem, "Front/Vertical/Left/Seg01/X/Sensor")

    logger = tools.Logger()
    dico["logger"] = logger

    def fin():
        """Method executed after a joint test."""
        result_file_path = "/".join(
            [
                result_base_folder,
                "Vertical_Test"
            ]) + ".csv"
        logger.log_file_write(result_file_path)

    request.addfinalizer(fin)
    return dico


@pytest.fixture(scope="module")
def get_horizontal_x_segments(request, result_base_folder, dcm, mem, side):
    """
    Return a dictionary with several objects for
    each X coordinate of all horizontal segments
    """
    dico = {}
    for i in range(1, 10):
        dico["seg" + str(i)] = Laser(dcm, mem, side + "/Horizontal/Seg0"
                                     + str(i) + "/X/Sensor")
    for i in range(10, 16):
        dico["seg" + str(i)] = Laser(dcm, mem, side + "/Horizontal/Seg"
                                     + str(i) + "/X/Sensor")
    logger = tools.Logger()
    dico["logger"] = logger

    def fin():
        """Method executed after a joint test."""
        result_file_path = "/".join(
            [
                result_base_folder,
                side
            ]) + ".csv"
        logger.log_file_write(result_file_path)

    request.addfinalizer(fin)
    return dico


@pytest.fixture(scope="module")
def get_lasers_x_segments(request, result_base_folder, dcm, mem):
    """
    Return a dictionary with several objects for
    each X coordinate of all lasers segments
    """
    h_sides = ["Front", "Left", "Right"]
    v_sides = ["Left", "Right"]
    dico = {}
    for each in h_sides:
        for i in range(1, 10):
            dico["Horizontal_X_seg" + str(i) + "_" + each] = Laser(
                dcm, mem, each + "/Horizontal/Seg0" + str(i) + "/X/Sensor")
        for i in range(10, 16):
            dico["Horizontal_X_seg" + str(i) + "_" + each] = Laser(
                dcm, mem, each + "/Horizontal/Seg" + str(i) + "/X/Sensor")
    for each in v_sides:
        dico["Vertical_X_seg01_" + each] = Laser(
            dcm, mem, "Front/Vertical/" + each + "/Seg01/X/Sensor")
    for i in range(1, 4):
        dico["Shovel_X_seg" + str(i)] = Laser(
            dcm, mem, "Front/Shovel/Seg0" + str(i) + "/X/Sensor")

    logger_dist = tools.Logger()
    logger_error = tools.Logger()
    dico["logger_dist"] = logger_dist
    dico["logger_error"] = logger_error

    def fin():
        """Method executed after a joint test."""
        result_file_path1 = "/".join(
            [
                result_base_folder,
                "Dance_test_distances"
            ]) + ".csv"
        logger_dist.log_file_write(result_file_path1)

    request.addfinalizer(fin)
    return dico


@pytest.fixture(scope="session")
def wakeup(request, motion):
    """
    Make the robot wakeUp at the beginning
    of the test and go to rest at the end
    """
    # Remove the rotation due to the Active Diagnosis
    motion.setMotionConfig([["ENABLE_MOVE_API", False]])
    motion.wakeUp()
    motion.setMotionConfig([["ENABLE_MOVE_API", True]])

    def fin():
        """Method automatically executed at the end of the test"""
        motion.rest()
    request.addfinalizer(fin)
