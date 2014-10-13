'''
Created on October 13, 2014

@author: amartin

[Description]
This script allows the visualization of
the inertial base datas in real time.

[Initial conditions]
Robot in rest position.
'''
from real_time_display_utils import display_inertialbase_data


def test_display(inertialbase_objects_rt):
    """
    Test main function
    """
    print "test is running ..."
    display_inertialbase_data(inertialbase_objects_rt)

