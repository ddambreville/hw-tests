import pytest
import time
import threading
import uuid
import subdevice


class Log(threading.Thread):

    """
    Class to log during test
    """

    def __init__(self, dcm, mem, event, file_name):
        """
        @dcm                    : proxy to DCM (object)
        @mem                    : proxy to ALMemory (object)
        @event                  : event (object)
        @file_name              : name of log file (string)
        """

        threading.Thread.__init__(self)
        self._mem = mem
        self._event = event
        self._file_name = file_name

        self._wheelb_speed_act = subdevice.WheelSpeedActuator(
            dcm, mem, "WheelB")
        self._wheelfr_speed_act = subdevice.WheelSpeedActuator(
            dcm, mem, "WheelFR")
        self._wheelfl_speed_act = subdevice.WheelSpeedActuator(
            dcm, mem, "WheelFL")
        self._wheelb_speed_sen = subdevice.WheelSpeedSensor(
            dcm, mem, "WheelB")
        self._wheelfr_speed_sen = subdevice.WheelSpeedSensor(
            dcm, mem, "WheelFR")
        self._wheelfl_speed_sen = subdevice.WheelSpeedSensor(
            dcm, mem, "WheelFL")

        self._end = False

    def run(self):
        """ Log """

        log_file = open(self._file_name + ".csv", 'w')
        line_to_write = ",".join([
            "Time",
            "Event",
            "WheelBSpeedAct",
            "WheelFRSpeedAct",
            "WheelFLSpeedAct",
            "WheelBSpeedSen",
            "WheelFRSpeedSen",
            "WheelFLSpeedSen"
        ]) + "\n"
        log_file.write(line_to_write)
        log_file.flush()

        time_init = time.time()
        while not self._end:
            elapsed_time = time.time() - time_init
            line_to_write = ",".join([
                str(elapsed_time),
                str(self._event.flag_event),
                str(self._wheelb_speed_act.value),
                str(self._wheelfr_speed_act.value),
                str(self._wheelfl_speed_act.value),
                str(self._wheelb_speed_sen.value),
                str(self._wheelfr_speed_sen.value),
                str(self._wheelfl_speed_sen.value)
            ]) + "\n"
            log_file.write(line_to_write)
            log_file.flush()

            time.sleep(0.1)

    def stop(self):
        """ To stop logging """
        self._end = True


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


def test_robollomes_water(dcm, mem, motion, session, motion_wake_up,
                          speed):
    """
    Test rollonomes with dances or behaviors : no fall down.
    Launch requested dances (cf associated config file).
    Assert True is no fall down detected.

    @dcm            ; proxu to DCM (object)
    @mem            : proxy to ALMemory (object)
    @motion         ; proxy to ALMotion (object)
    @session        : Session in qi (object)
    @albehaviormanager  : proxy to ALBehavioManager (object)
    @motion_wake_up : robot does is wakeUp
    @speed_value    : dictionnary {"speed":value} (dictionnary)
    """

    # Subcribe to module
    expected = {"ALMotion/RobotIsFalling": 1}
    module_name = "EventChecker_{}_".format(uuid.uuid4())
    robot_is_falling = EventModule(mem, "ALMotion/RobotIsFalling")
    module_id = session.registerService(module_name, robot_is_falling)
    robot_is_falling.subscribe(module_name, expected)

    log = Log(dcm, mem, robot_is_falling, str(speed) + ".csv")
    log.start()

    while True:
        try:
            motion.move(speed, 0, 0)
        except KeyboardInterrupt:
            break

    while True:
        try:
            motion.move(0, 0, speed)
        except KeyboardInterrupt:
            break

    log.stop()
    session.unregisterService(module_id)

    if robot_is_falling.flag:
        assert False
