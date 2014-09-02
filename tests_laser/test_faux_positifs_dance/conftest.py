'''
Created on August 22, 2014

@author: amartin
'''

import tools
import pytest
from subdevice import Laser
import ConfigParser


@pytest.fixture(scope="session")
def config_test():
    """
    Reading test configuration file
    """
    cfg = ConfigParser.ConfigParser()
    cfg.read('TestConfig.cfg')
    return cfg


@pytest.fixture(params=tools.use_section("TestConfig.cfg", "Dance"))
def dance(request):
    """
    Fixture which return the dance
    """
    return request.param


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


@pytest.fixture(scope="module")
def get_lasers_x_segments(request, result_base_folder, dcm, mem):
    """
    Put the X coordinates of each laser in a dictionary
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

    logger = tools.Logger()
    dico["logger"] = logger

    def fin():
        """Method executed after a joint test."""
        result_file_path = "/".join(
            [
                result_base_folder,
                "Dance_test"
            ]) + ".csv"
        logger.log_file_write(result_file_path)

    request.addfinalizer(fin)
    return dico
