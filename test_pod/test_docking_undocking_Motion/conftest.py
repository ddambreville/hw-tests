'''
Created on October 16, 2014

@author: amartin
'''

import ConfigParser
import pytest
from subdevice import ChargingStationSensor, Bumper, BatteryCurrentSensor, \
    JointPositionActuator, JointPositionSensor, \
    WheelSpeedActuator, WheelSpeedSensor, Bumper, Laser, Sonar
import qha_tools
import threading
import time
from math import pi
import os
from termcolor import colored


def returnlist(char):
    """
    Make liste
    """
    liste = []
    i = 0
    for numb, each in enumerate(char):
        if each == " ":
            liste.append(float(char[i: numb]))
            i = numb + 1
        elif numb == len(char) - 1:
            liste.append(float(char[i: numb + 1]))
            i = numb + 1
    return liste


def all_coord():
    """
    Return all the initial robot positions
    """
    coords = []
    cpt = 0
    cfg = ConfigParser.ConfigParser()
    cfg.read('TestConfig.cfg')
    angles = cfg.get('TestConfig', 'Angles')
    distances = cfg.get('TestConfig', 'Distances')
    cycles = int(cfg.get('TestConfig', 'Cycles'))
    liste_angles = returnlist(angles)
    liste_distances = returnlist(distances)
    while cpt < cycles:
        for angle in liste_angles:
            for distance in liste_distances:
                coords.append(
                    [float(distance), float(angle), cpt])
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
        "Distance,Angle,robot_on_charging_station,BackBumper,battery_current, \
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
                if "Wheel" in each or "Bumper" in each or \
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


@pytest.fixture(scope="session")
def sensor_logger(request, result_base_folder, dcm, mem):
    """
    Return a dictionary with several objects for
    each X coordinate of all lasers segments
    """
    thread_flag = threading.Event()
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
    logger = qha_tools.Logger()

    def log(logger, bag):
        """
        Docstring
        """
        t_0 = time.time()
        while not thread_flag.is_set():
            sensor_value = bag.value
            for each in sensor_value.keys():
                logger.log((each, sensor_value[each]))

            logger.log(("Time", time.time() - t_0))
        time.sleep(0.01)
    log_thread = threading.Thread(target=log, args=(logger, bag))
    log_thread.start()

    def fin():
        """Method executed after a joint test."""
        thread_flag.set()
        result_file_path1 = "/".join(
            [
                result_base_folder,
                "Front_sensors_distances"
            ]) + ".csv"
        logger.log_file_write(result_file_path1)

    request.addfinalizer(fin)
    return dico
