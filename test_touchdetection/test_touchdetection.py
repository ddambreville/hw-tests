import pytest
import qha_tools
import subdevice
import threading
import time
import plot_touchdetection
import uuid


def move_joint(name, value, speed, motion):
    motion.angleInterpolationWithSpeed(name, value, speed)


def set_position(dcm, mem, motion, section):
    datas = qha_tools.read_section("touch_detection.cfg", section)

    for name, value in datas.items():
        if value[0] == "max":
            sub = subdevice.SubDevice(dcm, mem, name + "/Position/Actuator")
            angle = float(sub.maximum)
        elif value[0] == "min":
            sub = subdevice.SubDevice(dcm, mem, name + "/Position/Actuator")
            angle = float(sub.minimum)
        else:
            angle = float(value[0])
        move_joint(name, angle, 0.1, motion)


def movement(joint_name, joint_min, joint_max, joint_temp, parameters,
             motion):

    if parameters["TouchStop"][0] == True:
        amplitude = 1
    else:
        amplitude = 0.90
    print(joint_name)

    time_init = time.time()
    while (time.time() - time_init) < float(parameters["TimeByJoint"][0]) and\
            joint_temp.value < int(parameters["TemperatureMax"][0]):
        move_joint(
            joint_name,
            joint_max * amplitude,
            float(parameters["Speed"][0]),
            motion
        )
        move_joint(
            joint_name,
            joint_min * amplitude,
            float(parameters["Speed"][0]),
            motion
        )
    if joint_temp.value > int(parameters["TemperatureMax"][0]):
        print "Joint too hot !!!"


class EventModule:

    """
    Module to launch function if event detected.
    """

    def __init__(self, mem):
        self.mem = mem
        self._flag_event = 0
        self._flag = False

    def subscribe(self, module_name, events):
        for k in events.keys():
            self.mem.subscribeToEvent(k, module_name, "_event_detected")

    def _event_detected(self, event_name, value, comment=""):
        event_detected = str(self.mem.getData("TouchChanged"))
        print("Event detected : " + event_detected)
        if "True" in event_detected:
            self._flag_event = 1
            self._flag = True
        else:
            self._flag_event = 0

    def _get_flag_event(self):
        return self._flag_event

    def _get_flag(self):
        return self._flag

    flag_event = property(_get_flag_event)
    flag = property(_get_flag)


def test_touchdetection(dcm, mem, motion, session, motion_wake_up,
                        remove_safety, parameters, test_objects_dico):
    """
    Test touch detection.
    """
    expected = {"TouchChanged": 1}
    module_name = "EventChecker_{}_".format(uuid.uuid4())
    touchdetection = EventModule(mem)
    module_id = session.registerService(module_name, touchdetection)
    touchdetection.subscribe(module_name, expected)

    # Objects creation
    joint = test_objects_dico["jointName"]
    joint_position_actuator = test_objects_dico["jointPositionActuator"]
    joint_position_sensor = test_objects_dico["jointPositionSensor"]
    joint_speed_actuator = test_objects_dico["jointSpeedActuator"]
    joint_speed_sensor = test_objects_dico["jointSpeedSensor"]
    joint_temperature = test_objects_dico["jointTemperature"]

    # Go to initial position
    set_position(dcm, mem, motion, "ReferencePosition")

    # Send datas
    plot = plot_touchdetection.Plot(
        joint,
        mem,
        touchdetection,
        joint_position_actuator,
        joint_position_sensor,
        joint_speed_actuator,
        joint_speed_sensor,
        float(parameters["LimitErrorPosition"][0]),
        float(parameters["LimitErrorSpeed"][0])
    )
    plot.start()

    # Movement
    set_position(dcm, mem, motion, joint)
    time.sleep(2)

    movement(joint,
             joint_position_actuator.minimum,
             joint_position_actuator.maximum,
             joint_temperature,
             parameters,
             motion
             )

    # Stop send datas
    plot.stop()
    time.sleep(0.25)

    if touchdetection.flag:
        assert False
