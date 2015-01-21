import pytest
import qha_tools
import subdevice
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


def move(motion, speed, direction):
    motion.move(float(speed) * int(direction["x"][0]),
                float(speed) * int(direction["y"][0]),
                float(speed) * int(direction["z"][0])
                )


def test_sensors_env_004(robot_ip, dcm, mem, motion, session,
                         motion_wake_up, parameters, direction,
                         speed):
    """
    Docstring
    """
    expected = {"ALMotion/MoveFailed": 1}
    module_name = "EventChecker_{}_".format(uuid.uuid4())
    movefailed = EventModule(mem)
    module_id = session.registerService(module_name, movefailed)
    movefailed.subscribe(module_name, expected)

    flag_test = False

    # Sensors
    sensors_list = qha_tools.read_section("sensors.cfg", "Sensors")
    ir_right = subdevice.InfraredSpot(dcm, mem, "Right")
    ir_left = subdevice.InfraredSpot(dcm, mem, "Left")

    log = multi_logger.Logger(
        robot_ip,
        "multi_logger.cfg",
        0.1,
        "Direction" + str(direction) + " - " + str(speed) + ".csv")
    log.log()

    # Movement
    move(motion, speed,
         qha_tools.read_section("env_004.cfg", "Direction" + direction)
         )

    time.sleep(1)

    while not movefailed.flag and not flag_test:
        for sensor in sensors_list:
            if mem.getData(sensor) < float(parameters["distance"][0]):
                print(sensor)
                motion.stopMove()
                flag_test = True
        # if ir_right.value == 1:
        #     print("IR_Right")
        #     motion.stopMove()
        #     flag_test = True
        # if ir_left.value == 1:
        #     print("IR_Left")
        #     motion.stopMove()
        #     flag_test = True

    log.stop()

    session.unregisterService(module_id)

    assert flag_test
