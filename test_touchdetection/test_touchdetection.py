import pytest
import qha_tools
import subdevice
import threading
import time
import plot_touchdetection
import uuid


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


def set_position(dcm, mem, motion, section):
    """
    Put robot in initial position.
    No return.

    @dcm        : proxy to DCM (object)
    @mem        : proxy to ALMemory (object)
    @motion     : proxy to ALMotion (object)
    @section    : name of section to read in config file (string)
    """

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


def movement(joint_name, joint_min, joint_max, joint_temp, speed,
             mechanical_stop, number, temp_max, motion):
    """
    Cycle of joint movement.
    Assert false if max temperature is reached.
    Else no return

    @joint_name         : name of joint to move (string)
    @joint_min          : minimal joint position (float)
    @joint_max          : maximal joint position (float)
    @joint_temp         : joint temperature object (object)
    @ speed             : movement speed (float in [0,1])
    @mechanical_stop    : touch mecanical stop (boolean)
    @number             : number of movement (integer)
    @temp_max           : maximal joint temperature permitted (integer)
    @motion             : proxy to ALMotion (object)
    """

    if mechanical_stop:
        amplitude = 1
    else:
        amplitude = 0.90

    movement_number = 0

    while movement_number < number:
        move_joint(
            joint_name,
            joint_max * amplitude,
            speed,
            motion
        )
        move_joint(
            joint_name,
            joint_min * amplitude,
            speed,
            motion
        )
        movement_number += 1
        if joint_temp.value > temp_max:
            print "Joint too hot !!!"
            print "Do again the test with a lower maximal temperature to start"
            assert False


class EventModule(object):

    """
    Module to launch function if event detected.

    @mem        : proxy to ALMemory (object)
    """

    def __init__(self, mem):
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


def test_touchdetection(dcm, mem, motion, session, motion_wake_up,
                        remove_safety, parameters, speed_value,
                        test_objects_dico):
    """
    Test touch detection : no false positive test.
    Move joints at different speeds (cf associated config file)
    Assert True if no TouchChanged event is detected.

    @dcm            : proxy to DCM (object)
    @mem            : proxy to ALMemory (object)
    @motion         : proxy to ALMotion (object)
    @session        : Session in qi (object)
    @motion_wake_up : robot does is wakeUp
    @remove_safety  : remove safety
    @parameters     : dictionnary {"parameter":value} from config file
                      (dictionnary)
    @speed_value    : dictionnary {"speed":value}
                      (dictionnary)
    @test_objects_dico : dictionnary {"Name":object} (dictionnary)
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
    speed = speed_value["Speed"]

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
        joint_temperature,
        float(parameters["LimitErrorPosition"][0]),
        float(parameters["LimitErrorSpeed"][0])
    )
    plot.start()

    print("\n\nJoint : " + joint + " - Speed : " + str(speed) + "\n")

    # Verify joint not too hot
    # If too hot, remove stiffness and wait
    while joint_temperature.value > \
            int(parameters["TemperatureMaxToStart"][0]):
        motion._setStiffnesses("Body", 0.0)
        print("Joint too hot : " + str(joint_temperature.value))
        print("-> Wait " + str(parameters["TimeWait"][0]) + "s")
        time.sleep(int(parameters["TimeWait"][0]))
    motion._setStiffnesses("Body", 1.0)

    # Move ElbowYaw needs to raise ShoulderRoll
    # So verify ShoulderRoll temperature
    if joint == "RElbowYaw":
        rshoulderroll_temp = subdevice.JointTemperature(
            dcm, mem, "RShoulderRoll")
        while rshoulderroll_temp.value > \
                int(parameters["TemperatureMaxToStart"][0]):
            print "RShoulderRoll too hot -> Wait"
            time.sleep(int(parameters["TimeWait"][0]))
    if joint == "LElbowYaw":
        lshoulderroll_temp = subdevice.JointTemperature(
            dcm, mem, "LShoulderRoll")
        while lshoulderroll_temp.value > \
                int(parameters["TemperatureMaxToStart"][0]):
            print "LShoulderRoll too hot -> Wait"
            time.sleep(int(parameters["TimeWait"][0]))

    # Movement
    set_position(dcm, mem, motion, joint)
    time.sleep(2)

    movement(joint,
             joint_position_actuator.minimum,
             joint_position_actuator.maximum,
             joint_temperature,
             speed,
             bool(parameters["MechanicalStop"][0]),
             int(parameters["MovementNumberByJoint"][0]),
             int(parameters["TemperatureMax"][0]),
             motion
             )

    # Stop send datas
    plot.stop()
    time.sleep(0.25)

    session.unregisterService(module_id)

    if touchdetection.flag:
        assert False
