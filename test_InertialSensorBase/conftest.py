#-*- coding: iso-8859-15 -*-

'''
Created on September 29, 2014

@author: amartin
'''

import tools
import pytest
from subdevice import InertialSensorBase


@pytest.fixture(scope="module")
def get_accelerometer_objects(request, result_base_folder, dcm, mem):
    """
    Return a dictionary with several objects for
    each accelerometer of the inertial base
    """
    dico = {}
    dico["Acc_x"] = InertialSensorBase(
        dcm, mem, "AccelerometerX")
    dico["Acc_y"] = InertialSensorBase(
        dcm, mem, "AccelerometerY")
    dico["Acc_z"] = InertialSensorBase(
        dcm, mem, "AccelerometerZ")
    logger = tools.Logger()
    dico["logger"] = logger

    def fin():
        """Method executed after a joint test."""
        result_file_path = "/".join(
            [
                result_base_folder,
                "Accelerometer_Log"
            ]) + ".csv"
        logger.log_file_write(result_file_path)

    request.addfinalizer(fin)
    return dico


@pytest.fixture(scope="module")
def get_all_inertialbase_objects(request, result_base_folder, dcm, mem):
    """
    Return a dictionary with several objects for
    each sensor value of the inertial base
    """
    dico = {}
    coord = ["X", "Y", "Z"]
    for each in coord:
        dico["Acc" + each] = InertialSensorBase(
            dcm, mem, "Accelerometer" + each)
        dico["Angle" + each] = InertialSensorBase(
            dcm, mem, "Angle" + each)
        dico["Gyr" + each] = InertialSensorBase(
            dcm, mem, "Gyr" + each)
    logger = tools.Logger()
    dico["logger"] = logger

    def fin():
        """Method executed after a joint test."""
        result_file_path = "/".join(
            [
                result_base_folder,
                "InertialBase_Log"
            ]) + ".csv"
        logger.log_file_write(result_file_path)

    request.addfinalizer(fin)
    return dico
