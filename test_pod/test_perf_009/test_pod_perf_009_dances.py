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


def run_behavior(albehaviormanager, behavior_name):
    """
    Funtion to run behavior.
    No return.

    @albehaviormanager  : prxy to ALBehaviorManager (obkect)
    @behavior_name      : name of the behavior ro run (string)
    """
    # Verify behavior existing
    if albehaviormanager.isBehaviorPresent(behavior_name):
        albehaviormanager.runBehavior(behavior_name)
    else:
        print("\n\nBehavior " + behavior_name + "is not present")
        print("Add the behavior and throw again")
        assert False


def test_robollomes_with_dances(dcm, mem, session, albehaviormanager,
                                motion_wake_up, behaviors):
    """
    Test rollonomes with dances or behaviors : no fall down.
    Launch requested dances (cf associated config file).
    Assert True is no fall down detected.

    @mem            : proxy to ALMemory (object)
    @session        : Session in qi (object)
    @albehaviormanager  : proxy to ALBehaviorManager (object)
    @motion_wake_up : robot does is wakeUp
    @behaviors          : dictionnary {"name":value} (dictionnary)
    """

    # Subcribe to module
    expected = {"ALMotion/RobotIsFalling": 1}
    module_name = "EventChecker_{}_".format(uuid.uuid4())
    robot_is_falling = EventModule(mem, "ALMotion/RobotIsFalling")
    module_id = session.registerService(module_name, robot_is_falling)
    robot_is_falling.subscribe(module_name, expected)

    behavior = behaviors["Name"]
    list_behaviors = qha_tools.use_section("pod_perf_009.cfg", behavior)

    for k in list_behaviors:
        log = log_pod.Log(dcm, mem, robot_is_falling, k + ".csv")
        log.start()
        run_behavior(albehaviormanager, k)
        log.stop()

    session.unregisterService(module_id)

    if robot_is_falling.flag:
        assert False
