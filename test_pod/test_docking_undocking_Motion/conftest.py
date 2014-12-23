'''
Created on October 16, 2014

@author: amartin
'''

import pytest
from subdevice import ChargingStationSensor, Bumper, BatteryCurrentSensor, \
    JointPositionActuator, JointPositionSensor, \
    WheelSpeedActuator, WheelSpeedSensor, Bumper
import qha_tools
import threading
import time
from math import pi
import os
from termcolor import colored

CYCLES = 2


def all_coord():
    """
    Return all the initial robot positions
    """
    coords = []
    cpt = 0
    dist = [0, 0.4, 1]
    while cpt < CYCLES:
        for x_coord in dist:
            coords.append([x_coord, 0, cpt])
        cpt = cpt + 1
    return coords


@pytest.fixture(scope="session")
def get_dict(request):
    """
    Docstring
    """
    my_dict = {"leaveStation": [], "lookForStation": [],
               "moveInFrontOfStation": [], "dockOnStation": []}

    def fin():
        """
        Docstring
        """
        print "\n"
        for key in my_dict.keys():
            cpt_fail = 0
            cpt_pass = 0
            for each in my_dict[key]:
                if each == True:
                    cpt_pass = cpt_pass + 1
                else:
                    cpt_fail = cpt_fail + 1
            print colored(key, "yellow")
            print "nb True = " + str(cpt_pass)
            print "nb False = " + str(cpt_fail) + "\n"
    request.addfinalizer(fin)
    return my_dict


@pytest.fixture(scope="session")
def csv_file():
    """
    Docstring
    """
    output = os.path.abspath("log_test.csv")
    log_file = open(output, 'w')
    log_file.write(
        "Angle,robot_on_charging_station,BackBumper,battery_current, \
        leaveStation_OK, leaveStation_NOK, lookForStation_OK, \
        lookForStation_NOK, moveInFrontOfStation_OK, moveInFrontOfStation_NOK, \
        dockOnStation_OK, dockOnStation_NOK\n"
    )

    return log_file


@pytest.fixture(params=all_coord())
def coord(request):
    """
    Perform the test for different initial position of the robot
    """
    return request.param


@pytest.fixture(scope="session")
def get_pod_objects(dcm, mem):
    """
    Return a dictionary with several objects for
    POD test
    """
    dico = {}
    dico["robot_on_charging_station"] = ChargingStationSensor(dcm, mem)
    dico["backbumper"] = Bumper(dcm, mem, "Back")
    dico["battery_current"] = BatteryCurrentSensor(dcm, mem)
    logger = qha_tools.Logger()
    dico["logger"] = logger
    return dico


@pytest.fixture(scope="session")
def log_joints(request, result_base_folder, dcm, mem, motion):
    """
    Return a dictionary with several objects for
    POD test
    """
    thread_flag = threading.Event()
    bag = qha_tools.Bag(mem)
    for each in motion.getBodyNames("Body"):
        if "Wheel" in each:
            bag.add_object(each + "_Actuator",
                           WheelSpeedActuator(dcm, mem, each))
            bag.add_object(each + "_Sensor",
                           WheelSpeedSensor(dcm, mem, each))
        else:
            bag.add_object(each + "_Actuator",
                           JointPositionActuator(dcm, mem, each))
            bag.add_object(each + "_Sensor",
                           JointPositionSensor(dcm, mem, each))
    bag.add_object("BackBumper", Bumper(dcm, mem, "Back"))
    bag.add_object(
        "robot_on_charging_station", ChargingStationSensor(dcm, mem))
    bag.add_object("battery_current", BatteryCurrentSensor(dcm, mem))
    logger = qha_tools.Logger()

    def log(logger, bag):
        """
        Docstring
        """
        t_0 = time.time()
        while not thread_flag.is_set():
            joints_value = bag.value
            for each in joints_value.keys():
                if "Wheel" in each or "Bumper" in each  or \
                        "charging" in each or "battery" in each:
                    logger.log((each, joints_value[each]))
                else:
                    logger.log((each, joints_value[each] * (180 / pi)))

            logger.log(("Time", time.time() - t_0))
        time.sleep(0.01)

    log_thread = threading.Thread(target=log, args=(logger, bag))
    log_thread.start()

    def fin():
        """
        Docstring
        """
        thread_flag.set()
        result_file_path = "/".join(
            [
                result_base_folder,
                "Joint_Log"
            ]) + ".csv"
        logger.log_file_write(result_file_path)
    request.addfinalizer(fin)
