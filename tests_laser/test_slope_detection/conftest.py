#-*- coding: iso-8859-15 -*-

'''
Created on September 23, 2014

@author: amartin
'''


import pytest
from subdevice import Laser
import qha_tools
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
def get_slope_segments(request, result_base_folder, dcm, mem):
    """
    Return a dictionary with several objects for
    each X coordinate of all horizontal segments
    """
    dico = {}
    dico["Left_Inclinaison"] = Laser(
        dcm, mem, "Front/Vertical/Left/Slope/Inclination/Sensor")
    dico["Left_Distance"] = Laser(
        dcm, mem, "Front/Vertical/Left/Slope/X/Sensor")
    dico["Right_Inclinaison"] = Laser(
        dcm, mem, "Front/Vertical/Right/Slope/Inclination/Sensor")
    dico["Right_Distance"] = Laser(
        dcm, mem, "Front/Vertical/Right/Slope/X/Sensor")

    logger = qha_tools.Logger()
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
