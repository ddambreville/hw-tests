'''
Created on October 16, 2014

@author: amartin
'''

import pytest
from subdevice import ChargingStationSensor, Bumper, BatteryCurrentSensor
import tools


def all_coord():
    """
    Return all the initial robot positions
    """
    coords = []
    for y in range(-1, 2):
        coords.append([0.5, 0.4 * y])
    return coords


@pytest.fixture(params=all_coord())
def coord(request):
    """
    Perform the test for different initial position of the robot
    """
    return request.param


@pytest.fixture(scope="session")
def get_pod_objects(request, result_base_folder, dcm, mem):
    """
    Return a dictionary with several objects for
    POD test
    """
    dico = {}
    dico["robot_on_charging_station"] = ChargingStationSensor(dcm, mem)
    dico["backbumper"] = Bumper(dcm, mem, "Back")
    dico["battery_current"] = BatteryCurrentSensor(dcm, mem)
    logger = tools.Logger()
    dico["logger"] = logger

    def fin():
        """Method executed after a joint test."""
        result_file_path = "/".join(
            [
                result_base_folder,
                "Pod_Log"
            ]) + ".csv"
        logger.log_file_write(result_file_path)

    request.addfinalizer(fin)
    return dico
