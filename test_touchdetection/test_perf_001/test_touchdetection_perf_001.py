import pytest
import qha_tools
import subdevice
import threading
import time
import uuid
import plot_touchdetection
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


def verify_joint_temperature(dcm, mem, motion, joint, joint_temperature,
                             temp_max_to_start, time_wait):
    # Verify joint not too hot
    # If too hot, remove stiffness and wait
    while joint_temperature.value > temp_max_to_start:
        motion._setStiffnesses("Body", 0.0)
        print("Joint too hot : " + str(joint_temperature.value))
        print("-> Wait " + str(time_wait) + "s")
        time.sleep(time_wait)
    motion._setStiffnesses("Body", 1.0)

    # Move ElbowYaw needs to raise ShoulderRoll
    # So verify ShoulderRoll temperature
    if joint == "RElbowYaw":
        rshoulderroll_temp = subdevice.JointTemperature(
            dcm, mem, "RShoulderRoll")
        while rshoulderroll_temp.value > temp_max_to_start:
            print "RShoulderRoll too hot -> Wait"
            time.sleep(time_wait)
    if joint == "LElbowYaw":
        lshoulderroll_temp = subdevice.JointTemperature(
            dcm, mem, "LShoulderRoll")
        while lshoulderroll_temp.value > temp_max_to_start:
            print "LShoulderRoll too hot -> Wait"
            time.sleep(time_wait)


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


def set_position(dcm, mem, motion, config_file, section):
    """
    Put robot in initial position.
    No return.

    @dcm        : proxy to DCM (object)
    @mem        : proxy to ALMemory (object)
    @motion     : proxy to ALMotion (object)
    @section    : name of section to read in config file (string)
    """

    datas = qha_tools.read_section(config_file, section)

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


def stiffness_part(motion, parts, value):
    """
    Remove stiffness for defined parts.
    No return.

    @motion     : proxy to ALMotion (object)
    @parts      : list of parts to remove stiffness
    """

    for k in parts:
        motion._setStiffnesses(k, value)


def movement(joint_name, joint_min, joint_max, joint_temp, speed,
             mechanical_stop, number, temp_max, motion, plot=None):
    """
    Cycle of joint movement.
    Assert false if max temperature is reached.
    No return.

    @joint_name         : name of joint to move (string)
    @joint_min          : minimal joint position (float)
    @joint_max          : maximal joint position (float)
    @joint_temp         : joint temperature object (object)
    @ speed             : movement speed (float in [0,1])
    @mechanical_stop    : touch mecanical stop (boolean)
    @number             : number of movement (integer)
    @temp_max           : maximal joint temperature permitted (integer)
    @motion             : proxy to ALMotion (object)
    @plot               : plot object (object)
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
            if plot != None:
                plot.stop()
            assert False


def test_touchdetection_perf_001(dcm, mem, motion, alleds, session,
                                 motion_wake_up, remove_sensors, parameters,
                                 speed_value, test_objects_dico, directions):
    """
    Test touch detection perf 001 : remove joint stiffness if touch detected.
    Move joints at different speeds (cf associated config file).
    Assert True if touch detected.

    @dcm            : proxy to DCM (object)
    @mem            : proxy to ALMemory (object)
    @motion         : proxy to ALMotion (object)
    @alleds         : proxy to ALLeds (object)
    @session        : Session in qi (object)
    @motion_wake_up : robot does is wakeUp
    @remove_sensors : remove Laser, Sonar & Asus sensors
    @parameters     : dictionnary {"parameter":value} from config file
                      (dictionnary)
    @speed_value    : dictionnary {"speed":value} (dictionnary)
    @test_objects_dico : dictionnary {"Name":object} (dictionnary)
    @directions     : dictionnary {"direction":value} (dictionnary)
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
    joint_hardness = test_objects_dico["jointHardness"]
    speed = speed_value["Speed"]
    direction = directions["Direction"]

    print("Joint : " + joint + " - Direction : " + direction)

    alleds.fadeRGB("FaceLeds", "red", 0)

    # Go to reference position
    set_position(dcm, mem, motion, "perf_001.cfg",
                 "ReferencePosition")

    # Plot datas
    # plot = plot_touchdetection.Plot(
    #     joint,
    #     mem,
    #     touchdetection,
    #     joint_position_actuator,
    #     joint_position_sensor,
    #     joint_speed_actuator,
    #     joint_speed_sensor,
    #     joint_temperature,
    #     joint_hardness,
    #     float(parameters["LimitErrorPosition"][0]),
    #     float(parameters["LimitErrorSpeed"][0]),
    #     int(parameters["TemperatureMaxToStart"][0]),
    #     int(parameters["TemperatureMax"][0])
    # )
    # plot.start()

    # Log datas
    log = log_touchdetection.Log(
        joint,
        speed,
        mem,
        touchdetection,
        joint_position_actuator,
        joint_position_sensor,
        joint_speed_actuator,
        joint_speed_sensor,
        joint_temperature,
        joint_hardness,
        float(parameters["LimitErrorPosition"][0]),
        float(parameters["LimitErrorSpeed"][0]),
        int(parameters["TemperatureMaxToStart"][0]),
        int(parameters["TemperatureMax"][0])
    )
    log.start()

    # Verify joint temperature to start test
    verify_joint_temperature(
        dcm, mem, motion, joint,
        joint_temperature, int(parameters["TemperatureMaxToStart"][0]),
        int(parameters["TimeWait"][0]))

    if direction == "MinToMax":
        # Initial position
        move_joint(joint, joint_position_actuator.minimum,
                   float(parameters["Speed"][0]), motion)
        time.sleep(2)

        alleds.fadeRGB("FaceLeds", "blue", 0)

        # Movement
        move_joint(joint, joint_position_actuator.maximum,
                   speed, motion)
    elif direction == "MaxToMin":
        # Initial position
        move_joint(joint, joint_position_actuator.maximum,
                   float(parameters["Speed"][0]), motion)
        time.sleep(2)

        alleds.fadeRGB("FaceLeds", "blue", 0)

        # Movement
        move_joint(joint, joint_position_actuator.minimum,
                   speed, motion)

    session.unregisterService(module_id)

    if touchdetection.flag:
        if joint_hardness.value == 0:
            # Remettre stiffness
            print "\nTouch detected - Stiffness decreased"
            flag = True
        else:
            print "\nTouch detected - Stiffness didn't decrease"
            flag = False
    else:
        print "\nTouch didn't detecte"
        flag = False

    alleds.fadeRGB("FaceLeds", "red", 0)

    # Put again stiffness in all robot's joint
    stiffness_part(motion, ["Body"], 1.0)

    # Go to reference position
    set_position(dcm, mem, motion, "perf_001.cfg",
                 "ReferencePosition")

    # plot.stop()
    log.stop()
    time.sleep(0.25)

    assert flag
