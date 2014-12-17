import pytest
import qha_tools
import subdevice
import threading
import time
import uuid
import plot_touchdetection


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


def move_joint(name, value, speed, motion):
    """
    Use motion to move joint.
    No return.

    @name      : name of joint to move (string)
    @value     : new position (float)
    @speed     : speed to move (float)
    @motion    : proxy to ALMotion (object)
    """

    motion.angleInterpolationWithSpeed(name, value, speed)


def test_touchdetection_perf_002(dcm, mem, motion, session, motion_wake_up,
                                 remove_sensors, move_arms_enabled, parameters,
                                 speed_value):
    """
    Test touch detection perf 003 : remove joint stiffness if arm is blocked.
    Rotate at different speed (cf associated config file).
    Assert True if touch detected.

    @dcm            : proxy to DCM (object)
    @mem            : proxy to ALMemory (object)
    @motion         : proxy to ALMotion (object)
    @session        : Session in qi (object)
    @motion_wake_up : robot does is wakeUp
    @remove_sensors : remove Laser, Sonar & Asus sensors
    @move_arms      : robot can move its arms when it moves base
    @ parameters    : dictionnary {"parameter":value} from config file
                      (dictionnary)
    @speed_value    : dictionnary {"speed":value} (dictionnary)
    """
    expected = {"TouchChanged": 1}
    module_name = "EventChecker_{}_".format(uuid.uuid4())
    touchdetection = EventModule(mem)
    module_id = session.registerService(module_name, touchdetection)
    touchdetection.subscribe(module_name, expected)

    plot = plot_touchdetection.Plot(
        dcm,
        mem,
        touchdetection,
        float(parameters["LimitErrorPosition"][0]),
        float(parameters["LimitErrorSpeed"][0]),
        int(parameters["TemperatureMax"][0]),
        int(parameters["TemperatureMaxToStart"][0]),
        parameters["FileName"][0]
    )
    plot.start()

    # Objects creation
    rshoulderroll_position_actuator = subdevice.JointPositionActuator(
        dcm, mem, "RShoulderRoll")
    lshoulderroll_position_actuator = subdevice.JointPositionActuator(
        dcm, mem, "LShoulderRoll")
    speed = speed_value["Speed"]

    move_joint("RShoulderRoll", rshoulderroll_position_actuator.minimum,
               float(parameters["Speed"][0]), motion)
    move_joint("LShoulderRoll", lshoulderroll_position_actuator.maximum,
               float(parameters["Speed"][0]), motion)

    while not touchdetection.flag:
        motion.move(0, 0, speed)

    time.sleep(2)

    plot.stop()

    session.unregisterService(module_id)