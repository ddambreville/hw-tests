'''
Created on October 17, 2014

@author: amartin

[Description]
Test docking-undocking using Motion

[Initial conditions]
Robot in rest position on the pod

'''
from qha_tools import switch, case
import test_utils
import time
from termcolor import colored


def test_pod_docking_undocking_Motion(dcm, mem, motion, alrecharge, coord,
                                      wakeup_no_rotation, get_pod_objects,
                                      csv_file, get_dict, remove_diagnosis):
    """
    Test docking-undocking using Motion
    """
    print coord[2]
    test_utils.init()
    log_file = csv_file
    test_utils.QUEUE.enqueue("leaveStation")
    time.sleep(5)
    my_dict = get_dict
    stop = False
    while stop == False:
        state = test_utils.QUEUE.dequeue()
        while switch(state):
            try:
                if case("leaveStation"):
                    test_utils.leave_station(alrecharge, my_dict)
                    break
                if case("leave_motion"):
                    test_utils.leave_motion(motion)
                    break
                if case("move"):
                    test_utils.move(motion, coord)
                    break
                if case("lookForStation"):
                    test_utils.look_for_station(alrecharge, my_dict)
                    break
                if case("moveInFrontOfStation"):
                    test_utils.move_front_station(alrecharge, my_dict)
                    break
                if case("dockOnStation"):
                    test_utils.dock_on_station(
                        alrecharge, get_pod_objects, my_dict)
                    break
                if case("log_data"):
                    test_utils.log_data(get_pod_objects, coord, log_file)
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
