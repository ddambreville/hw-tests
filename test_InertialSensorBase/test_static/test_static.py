'''
Created on September 29, 2014

@author: amartin

[Description]
This script tests the values returned by inertial base sensor
when the robot is static.

[Initial conditions]
Robot in rest position.
'''
import threading
from test_static_utils import check_error, record_inertialbase_data, wait



def test_static(get_all_inertialbase_objects, config_test):
    """
    Test main function which tests the inertial base sensor
    when the robot is static.
    """
    wait_thread = threading.Thread(target=wait, args=(config_test,))
    wait_thread.start()
    print "test is running ..."
    logger = record_inertialbase_data(get_all_inertialbase_objects, wait_thread)
    result = check_error(logger, config_test)
    assert 'Fail' not in result
