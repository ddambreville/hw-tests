import pytest
import time
import uuid
import multi_logger


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
        event_detected = str(self.mem.getData("ALMotion/MoveFailed"))
        print(str(event_detected))
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


def run_behavior(albehaviormanager, behavior_name):
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
        assert False


def test_robollomes_with_dances(robot_ip, mem, session, packagemanager,
                                albehaviormanager, stop_bootconfig,
                                motion_wake_up, behaviors):
    """
    Launch requested dances (cf associated config file).
    Assert True is no fall down detected.

    @mem            : proxy to ALMemory (object)
    @session        : Session in qi (object)
    @albehaviormanager  : proxy to ALBehavioManager (object)
    @motion_wake_up : robot does is wakeUp
    @behaviors          : dictionnary {"name":value} (dictionnary)
    """

    # Subcribe to module
    expected = {"ALMotion/MoveFailed": 1}
    module_name = "EventChecker_{}_".format(uuid.uuid4())
    obstacledetected = EventModule(mem)
    module_id = session.registerService(module_name, obstacledetected)
    obstacledetected.subscribe(module_name, expected)

    behavior = behaviors["Name"]
    packagemanager.install("/home/nao/behaviors_pkg/" + behavior + ".pkg")

    log = multi_logger.Logger(
        robot_ip,
        "multi_logger.cfg",
        0.1,
        behavior + ".csv")
    log.log()

    run_behavior(albehaviormanager, behavior)

    log.stop()

    packagemanager.removePkg(behavior)

    session.unregisterService(module_id)

    if obstacledetected.flag:
        assert True

    assert False
