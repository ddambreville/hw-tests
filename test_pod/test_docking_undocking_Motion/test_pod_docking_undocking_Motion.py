'''
Created on October 17, 2014

@author: amartin

[Description]
Test docking-undocking using Motion

[Initial conditions]
Robot in rest position on the pod

'''
from qha_tools import switch, case
from test_class import TestPodMotion
import time
from termcolor import colored


def test_pod_docking_undocking_Motion(dcm, mem, motion, alrecharge, coord,
                                      wakeup_no_rotation, get_pod_objects,
                                      csv_file, get_dict,
                                      sensor_logger, remove_diagnosis):
    """
    Test docking-undocking using Motion
    """
    print " distance = " + str(coord[0]) + " angle = " + str(coord[1])
    print coord[2]
    test_motion = TestPodMotion()
    test_motion.set_state("leaveStation")
    stop = False
    while stop == False:
        state = test_motion.get_state()
        while switch(state):
            try:
                if case("leaveStation"):
                    test_motion.leave_station(alrecharge, get_dict)
                    break
                if case("leave_motion"):
                    test_motion.leave_motion(motion)
                    break
                if case("move"):
                    test_motion.move(motion, coord)
                    break
                if case("lookForStation"):
                    test_motion.look_for_station(alrecharge, get_dict)
                    break
                if case("moveInFrontOfStation"):
                    test_motion.move_front_station(alrecharge, get_dict)
                    break
                if case("dockOnStation"):
                    test_motion.dock_on_station(
                        alrecharge, get_pod_objects, get_dict)
                    break
                if case("log_data"):
                    test_motion.log_data(get_pod_objects, coord, csv_file)
                    break
                if case("Fail"):
                    print colored("FAIL", "red")
                    stop = True
                    break
                if case("Arret"):
                    stop = True
                    print colored("PASS", "green")
                    break
            except KeyboardInterrupt:
                print "\r"
                stop = True
                assert False
        time.sleep(0.5)
