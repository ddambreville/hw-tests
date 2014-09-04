'''
Created on August 22, 2014

@author: amartin
'''

import pytest
from subdevice import Laser
import tools
import ConfigParser


@pytest.fixture(scope="session")
def config_test():
    """
    Reading test configuration file
    """
    cfg = ConfigParser.ConfigParser()
    cfg.read('TestConfig.cfg')
    return cfg


@pytest.fixture(params=tools.use_section("TestConfig.cfg", "Horizontal_Side"))
def side(request):
    """
    Fixture which returns the side(s) to be tested
    """
    return request.param


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
