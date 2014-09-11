'''
Created on September 5, 2014

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
