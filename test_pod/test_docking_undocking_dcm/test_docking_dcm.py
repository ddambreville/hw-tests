# -*- coding: utf-8 -*-

'''
Created on January 14, 2015

@author: amartin
'''

from test_class import TestPodDCM
import sys


def test_pod_dcm(dcm, mem, kill_motion, log_wheel):
    """
    Test robot docking/undocking with DCM
    """
    test_dcm = TestPodDCM(dcm, mem)
    test_dcm.initialisation()
    cpt = 0
    while cpt < int(test_dcm.nb_cycles):
        try:
            if test_dcm.wheel_hot == False:
                sys.stdout.write("cycle : " + str(cpt + 1) + chr(13))
                sys.stdout.flush()
                test_dcm.move_robot_x("Front")
                test_dcm.move_robot_x("Back")
                test_dcm.remove_stiffness()
                cpt = cpt + 1
                test_dcm.check_connection(cpt)
            else:
                pass
        except KeyboardInterrupt:
            break
    print "\n"
    test_dcm.end()
