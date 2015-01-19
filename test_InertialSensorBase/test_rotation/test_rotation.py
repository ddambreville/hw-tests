'''
Created on October 02, 2014

@author: amartin

[Description]
This script tests the Z Angle and the gyroscope Z speed returned by the
inertial base sensor.
'''

import threading
from test_rotation_utils import *


def test_rotation_distance(
        dcm, mem, motion, wakeup_no_rotation, get_all_inertialbase_objects,
        remove_safety, remove_diagnosis, config_test):
    """
    Test main function which tests the X distance
    of the horizontal lasers
    """
    motion_thread = threading.Thread(target=robot_motion, args=(
        motion, config_test))
    motion_thread.start()
    logger = record_inertialbase_data(
        get_all_inertialbase_objects, motion_thread, config_test)
    result = check_error(logger, config_test)
    assert "Fail" not in result
