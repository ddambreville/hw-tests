'''
Created on August 22, 2014

@author: amartin

[Description]
This script tests there aren't positives false on
the lasers (horizontal, vertical & shovel) during a dance.

[Initial conditions]
Place the robot in a free area, without anything around him.
Check that the dance(s) in the config file (TestConfig.cfg)
is(are) correctly installed.
'''

from test_class import TestDance


def test_faux_positifs_dance(
    mem, dcm, remove_diagnosis, wakeup, dance,
    remove_safety, behavior_manager, active_all_laser,
        sensor_objects, config_test):
    """
    Test function
    """
    test_dance = TestDance(
        behavior_manager, dance, sensor_objects, config_test)
    test_dance.robot_dance()
    test_dance.log()
    test_dance.check_datas()
    test_dance.print_error()
