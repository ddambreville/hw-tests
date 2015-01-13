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


def test_sensors_env_004(robot_ip, dcm, mem, motion, session,
                         motion_wake_up, parameters):
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
    # ir_right = subdevice.InfraredSpot(dcm, mem, "Right")
    # ir_left = subdevice.InfraredSpot(dcm, mem, "Left")

    log = multi_logger.Logger(
        robot_ip,
        "multi_logger.cfg",
        0.1,
        parameters["log_file_name"][0]
    )
    log.log()

    log_file = open("ObstacleDetection.csv", 'w')
    line_to_write = ",".join([
        "Time",
        "Sensor",
        "Distance"
    ]) + "\n"
    log_file.write(line_to_write)
    log_file.flush()

    # Movement
    motion.move(0, 0, float(parameters["speed"][0]))

    time.sleep(1)

    time_init = time.time()
    while True:
        elapsed_time = time.time() - time_init
        try:
            for sensor in sensors_list:
                if mem.getData(sensor) < float(parameters["distance2"][0]):
                    print(parameters["distance2"][0])
                    print(sensor)
                    line_to_write = ",".join([
                        str(elapsed_time),
                        sensor,
                        str(mem.getData(sensor))
                    ]) + "\n"
                    log_file.write(line_to_write)
                    log_file.flush()
                    flag_test = True
                elif mem.getData(sensor) < float(parameters["distance1"][0]):
                    print(parameters["distance1"][0])
                    print(sensor)
                    line_to_write = ",".join([
                        str(elapsed_time),
                        sensor,
                        str(mem.getData(sensor))
                    ]) + "\n"
                    log_file.write(line_to_write)
                    log_file.flush()
                    flag_test = True
                else:
                    line_to_write = ",".join([
                        str(elapsed_time),
                        "None",
                        "None"
                    ]) + "\n"
                    log_file.write(line_to_write)
                    log_file.flush()
            # if ir_right.value == 1:
            #     print("IR_Right")
            #     flag_test = True
            # if ir_left.value == 1:
            #     print("IR_Left")
            #     flag_test = True
            time.sleep(0.1)
            motion.move(0, 0, 0.3)
        except KeyboardInterrupt:
            break

    log.stop()

    session.unregisterService(module_id)

    assert flag_test
