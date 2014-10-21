'''
Created on October 17, 2014

@author: amartin

[Description]
Test docking-undocking using Motion

[Initial conditions]
Robot in rest position on the pod

'''
import time
from tools import switch, case
import test_utils


def test_pod_docking_undocking_Motion(dcm, mem, motion, alrecharge, coord,
                                      wakeup_no_rotation, get_pod_objects):
    """
    Test docking-undocking using Motion
    """
    test_utils.init()
    logger = get_pod_objects["logger"]
    test_utils.QUEUE.enqueue("leaveStation")
    stop = False
    time.sleep(1)
    while stop == False:
        state = test_utils.QUEUE.dequeue()
        while switch(state):
            if case("leaveStation"):
                test_utils.leave_station(alrecharge)
                break
            if case("move"):
                test_utils.move(motion, coord)
                break
            if case("lookForStation"):
                test_utils.look_for_station(alrecharge)
                break
            if case("moveInFrontOfStation"):
                test_utils.move_front_station(alrecharge)
                break
            if case("dockOnStation"):
                test_utils.dock_on_station(alrecharge)
                break
            if case("log_data"):
                test_utils.log_data(logger, get_pod_objects, coord)
                break
            if case("Fail"):
                assert False
                stop = True
            if case("Arret"):
                stop = True
                break
