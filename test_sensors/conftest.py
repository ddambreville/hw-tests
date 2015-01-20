#-*- coding: iso-8859-15 -*-

'''
Created on December 8, 2014

@author: amartin
'''


import pytest
from subdevice import Laser, Sonar
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


@pytest.fixture(scope="session")
def tolerance(config_test):
    """
    Return sensors tolerances
    """
    tolerances = {}
    for each in config_test.items('Tolerances'):
        tolerances[each[0]] = each[1]
    return tolerances


@pytest.fixture(scope="module")
def sensor_objects(request, result_base_folder, dcm, mem):
    """
    Return a dictionary with several objects for
    each X coordinate of all lasers segments
    """
    h_sides = ["Front", "Left", "Right"]
    v_sides = ["Left", "Right"]
    s_sides = ["Front", "Back"]
    bag = qha_tools.Bag(mem)
    dico = {}
    for each in h_sides:
        for i in range(1, 10):
            bag.add_object("Horizontal_X_seg" + str(i) + "_" + each, Laser(
                dcm, mem, each + "/Horizontal/Seg0" + str(i) + "/X/Sensor"))
        for i in range(10, 16):
            bag.add_object("Horizontal_X_seg" + str(i) + "_" + each, Laser(
                dcm, mem, each + "/Horizontal/Seg" + str(i) + "/X/Sensor"))
    for each in v_sides:
        bag.add_object("Vertical_X_seg01_" + each, Laser(
            dcm, mem, "Front/Vertical/" + each + "/Seg01/X/Sensor"))
    for each in s_sides:
        bag.add_object("Sonar_" + each, Sonar(
            dcm, mem, each))
    for i in range(1, 4):
        bag.add_object("Shovel_X_seg" + str(i), Laser(
            dcm, mem, "Front/Shovel/Seg0" + str(i) + "/X/Sensor"))
    logger_dist = qha_tools.Logger()
    logger_error = qha_tools.Logger()
    dico["logger_dist"] = logger_dist
    dico["logger_error"] = logger_error
    dico["bag"] = bag

    def fin():
        """Method executed after a joint test."""
        result_file_path1 = "/".join(
            [
                result_base_folder,
                "Front_sensors_distances"
            ]) + ".csv"
        logger_dist.log_file_write(result_file_path1)

    request.addfinalizer(fin)
    return dico
