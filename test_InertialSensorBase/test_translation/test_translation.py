'''
Created on October 13, 2014

@author: amartin

[Description]
This script tests the values returned by inertial base sensor
when the robot move.

[Initial conditions]
Robot in rest position.
'''
import threading
from test_translation_utils import record_inertialbase_data, robot_motion


def test_static(wakeup_no_rotation, remove_safety,
        remove_diagnosis, get_all_inertialbase_objects, config_test, motion):
    """
    Test main function which tests the inertial base sensor
    when the robot move (translation).
    """
    move_thread = threading.Thread(target=robot_motion, args=(
        config_test, motion))
    move_thread.start()
    print "test is running ..."
    record_inertialbase_data(get_all_inertialbase_objects, move_thread)
