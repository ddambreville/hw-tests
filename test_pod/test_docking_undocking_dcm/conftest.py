# -*- coding: utf-8 -*-

'''
Created on January 14, 2015

@author: amartin
'''
import pytest
import threading
import qha_tools
from subdevice import WheelSpeedActuator, WheelSpeedSensor, WheelCurrentSensor
import time


@pytest.fixture(scope="session")
def log_wheel(request, result_base_folder, dcm, mem):
    """
    Return a dictionary with several objects for
    POD test
    """
    thread_flag = threading.Event()
    bag = qha_tools.Bag(mem)
    wheels = ["WheelFR", "WheelFL", "WheelB"]
    for wheel in wheels:
        bag.add_object(
            wheel + "SpeedActuator", WheelSpeedActuator(dcm, mem, wheel))
        bag.add_object(
            wheel + "SpeedSensor", WheelSpeedSensor(dcm, mem, wheel))
        bag.add_object(
            wheel + "CurrentSensor", WheelCurrentSensor(dcm, mem, wheel))
    logger = qha_tools.Logger()

    def log(logger, bag):
        """
        Docstring
        """
        t_0 = time.time()
        while not thread_flag.is_set():
            wheel_value = bag.value
            for each in wheel_value.keys():
                logger.log((each, wheel_value[each]))
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
                "wheel_Log"
            ]) + ".csv"
        logger.log_file_write(result_file_path)
    request.addfinalizer(fin)
