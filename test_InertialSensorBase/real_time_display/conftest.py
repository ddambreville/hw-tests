'''
Created on October 13, 2014

@author: amartin
'''

import pytest
from subdevice import InertialSensorBase


@pytest.fixture(scope="module")
def inertialbase_objects_rt(dcm, mem):
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
    return dico
