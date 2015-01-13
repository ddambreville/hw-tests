import pytest
import qha_tools
import subdevice
import threading
import time
import uuid
import log_touchdetection


class EventModule(object):

    """
    Module which launch function if event detected.
    """

    def __init__(self, mem):
        """
        @mem        : proxy to ALMemory (object)
        """
        self.mem = mem
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
            self.mem.subscribeToEvent(k, module_name, "_event_detected")

    def _event_detected(self):
        """
        Function triggered when event is detected.
        Change flags.
        """
        event_detected = str(self.mem.getData("TouchChanged"))
        print("Event detected : " + event_detected)
        if "True" in event_detected:
            self._flag_event = 1
            self._flag = True
        else:
            self._flag_event = 0

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


def run_behavior(albehaviormanager, behavior_name, log):
    """
    Funtion to run behavior.
    No return.

    @behavior_name      : name of the behavior ro run (string)
    @plot               : plot object (object)
    """
    # Verify behavior existing
    if albehaviormanager.isBehaviorPresent(behavior_name):
        albehaviormanager.runBehavior(behavior_name)
    else:
        print("\n\nBehavior " + behavior_name + "is not present")
        print("Add the behavior and throw again")
        log.stop()
        assert False


def test_touchdetection_with_dances(dcm, mem, motion, session,
                                    albehaviormanager, motion_wake_up,
                                    parameters, behaviors):
    """
    Test rollonomes with dances or behaviors : no fall down.
    Launch requested dances (cf associated config file).
    Assert True is no fall down detected.

    @mem            : proxy to ALMemory (object)
    @session        : Session in qi (object)
    @albehaviormanager  : proxy to ALBehavioManager (object)
    @motion_wake_up : robot does is wakeUp
    @behaviors          : dictionnary {"name":value} (dictionnary)
    """

    # Subcribe to module
    expected = {"TouchChanged": 1}
    module_name = "EventChecker_{}_".format(uuid.uuid4())
    touchdetection = EventModule(mem)
    module_id = session.registerService(module_name, touchdetection)
    touchdetection.subscribe(module_name, expected)

    behavior = behaviors["Name"]

    log = log_touchdetection.Log(
        dcm,
        mem,
        touchdetection,
        float(parameters["LimitErrorPosition"][0]),
        float(parameters["LimitErrorSpeed"][0]),
        behavior + ".csv"
    )
    log.start()

    run_behavior(albehaviormanager, behavior, log)

    session.unregisterService(module_id)

    log.stop()

    motion._setStiffnesses("Body", 1.0)

    assert touchdetection.flag
