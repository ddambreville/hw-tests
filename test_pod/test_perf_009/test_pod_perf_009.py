import pytest
import time
import threading
import uuid
import qha_tools
import log_pod


class EventModule(object):

    """
    Module which launch function if event detected.
    """

    def __init__(self, mem, event):
        """
        @mem        : proxy to ALMemory (object)
        @event      : ALMemory key of the event expected (string)
        """
        self._mem = mem
        self._event_name = event
        self._flag_event = 0      # = 1 when event detected, else = 0
        self._flag = False        # True when event detected at least one time

    def subscribe(self, module_name, events):
        """
        Subscribe to event.
        Run function when event is detected.

        @module_name    : event module name
        @ events        : events expected (dictionnary)
        """
        for k in events.keys():
            self._mem.subscribeToEvent(k, module_name, "_event_detected")

    def _event_detected(self):
        """
        Function triggered when event is detected.
        Change flags.
        """
        event_detected = str(self._mem.getData(self._event_name))
        print("Event detected : " + event_detected)
        self._flag_event = 1
        self._flag = True

    def _get_flag_event(self):
        """
        Return flag event.
        """
        return self._flag_event

    def _get_flag(self):
        """
        Return flag.
        """
        return self._flag

    flag_event = property(_get_flag_event)
    flag = property(_get_flag)


def test_pod_with_dances(dcm, mem, motion, session, parameters):
    """
    Test pod during wakeUp : no base mouvement.
    Assert True is no fall down detected.

    @dcm            : proxt to DCM (object)
    @mem            : proxy to ALMemory (object)
    @motion         : proxy to ALMotion (object)
    @session        : Session in qi (object)
    @parameters     : dictionnary {"parameter":value} from config file
                      (dictionnary)
    """

    # Subcribe to module
    expected = {"ALMotion/RobotIsFalling": 1}
    module_name = "EventChecker_{}_".format(uuid.uuid4())
    robot_is_falling = EventModule(mem, "ALMotion/RobotIsFalling")
    module_id = session.registerService(module_name, robot_is_falling)
    robot_is_falling.subscribe(module_name, expected)

    log = log_pod.Log(dcm, mem, robot_is_falling, parameters["FileName"][0])
    log.start()

    motion.wakeUp()

    log.stop()

    motion.rest()
    session.unregisterService(module_id)

    if robot_is_falling.flag:
        assert False
