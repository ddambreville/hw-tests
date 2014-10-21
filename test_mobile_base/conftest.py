import pytest
import qha_tools
import subdevice
import threading
import time
import datetime
import os
import csv
from naoqi import ALProxy


@pytest.fixture(scope="session")
def leds(robot_ip, port):
    """
    Fixture which returns a proxy to ALLeds module
    """
    return ALProxy("ALLeds", robot_ip, port)


@pytest.fixture(scope="session")
def wait_time():
    """
    Returns a wait time [ms]
    """
    return int(qha_tools.read_parameter("config.cfg", "MobileBaseParameters",
                                    "wait_time"))


@pytest.fixture(scope="session")
def wait_time_bumpers():
    """
    Returns the time before checking bumpers again [ms]
    """
    return int(qha_tools.read_parameter("config.cfg", "MobileBaseParameters",
                                    "wait_time_bumpers"))


@pytest.fixture(scope="session")
def log_period():
    """
    Returns the log period [s]
    """
    return float(qha_tools.read_parameter("config.cfg", "MobileBaseParameters",
                                      "log_period"))


@pytest.fixture(scope="session")
def min_fraction():
    """
    Returns the minimum fraction speed for a wheel
    """
    return float(qha_tools.read_parameter("config.cfg", "MobileBaseParameters",
                                      "min_fraction"))


@pytest.fixture(scope="session")
def max_fraction():
    """
    Returns the maximum fraction speed for a wheel
    """
    return float(qha_tools.read_parameter("config.cfg", "MobileBaseParameters",
                                      "max_fraction"))


@pytest.fixture(scope="session")
def max_random():
    """
    Returns the maximum value for the rand funtion
    """
    return int(qha_tools.read_parameter("config.cfg", "MobileBaseParameters",
                                    "max_random"))


@pytest.fixture(scope="session")
def stop_robot(request, dcm, mem, wait_time):
    """
    Stops the robot at the end of the test
    """
    def fin():
        wheel_fr_speed_actuator = subdevice.WheelSpeedActuator(
            dcm, mem,"WheelFR")
        wheel_fl_speed_actuator = subdevice.WheelSpeedActuator(
            dcm, mem,"WheelFL")
        wheel_b_speed_actuator  = subdevice.WheelSpeedActuator(
            dcm, mem,"WheelB")
        wheel_fr_speed_actuator.qvalue = (0.0, 0)
        wheel_fl_speed_actuator.qvalue = (0.0, 0)
        wheel_b_speed_actuator.qvalue  = (0.0, 0)
        print "Robot stopped"
        qha_tools.wait(dcm, wait_time)

    request.addfinalizer(fin)


@pytest.fixture(scope="session")
def unstiff_joints(dcm, mem, wait_time):
    """
    Unstiff all joints except HipPitch, KneePitch and Wheels
    """
    joints = qha_tools.use_section("config.cfg", "JulietteJoints")
    for joint in joints:
        joint_hardness = subdevice.JointHardnessActuator(dcm, mem, joint)
        joint_hardness.qqvalue = 0.0
    qha_tools.wait(dcm, wait_time)


@pytest.fixture(scope="session")
def log_wheels_speed(request, dcm, mem, system, log_period):
    """
    Log wheels' speeds [rad/s] every 0.5s
    """
    wheel_fr_speed_sensor = subdevice.WheelSpeedSensor(
        dcm, mem, "WheelFR")
    wheel_fl_speed_sensor = subdevice.WheelSpeedSensor(
        dcm, mem, "WheelFL")
    wheel_b_speed_sensor  = subdevice.WheelSpeedSensor(
        dcm, mem, "WheelB")

    file_extension = "csv"
    robot_name = system.robotName()
    date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_type = "wheels_speeds"
    file_name = "-".join([robot_name, date, log_type])
    output = ".".join([file_name, file_extension])

    data = open(output, 'w')
    data.write(
            "Time (s)" + "," +
            "wheel FR speed [rad/s]" + "," +
            "wheel FL speed [rad/s]" + "," +
            "Wheel B speed [rad/s]" + "\n"
    )

    threading_flag = threading.Event()

    def log(threading_flag):
        cpt = 1
        time_init = time.time()
        while not threading_flag.is_set():
            line = ""
            if float(format((time.time() - time_init),
                     '.1f')) == (cpt * log_period):
                cpt += 1
                line += str(float(format((time.time() - time_init),
                         '.1f'))) + "," + \
                        str(wheel_fr_speed_sensor.value) + "," + \
                        str(wheel_fl_speed_sensor.value) + "," + \
                        str(wheel_b_speed_sensor.value) + "\n"
                data.write(line)
                data.flush()

    log_thread = threading.Thread(target=log, args=(threading_flag,))
    log_thread.start()

    def fin():
        threading_flag.set()

    request.addfinalizer(fin)


@pytest.fixture(scope="session")
def log_bumper_pressions(request, dcm, mem, system, wait_time_bumpers):
    """
       If one or more bumpers are pressed,
       it saves wheels' speeds [rad/s]
    """
    wheel_fr_speed_sensor = subdevice.WheelSpeedSensor(
        dcm, mem,"WheelFR")
    wheel_fl_speed_sensor = subdevice.WheelSpeedSensor(
        dcm, mem,"WheelFL")
    wheel_b_speed_sensor  = subdevice.WheelSpeedSensor(
        dcm, mem,"WheelB")

    bumper_right = subdevice.Bumper(dcm, mem, "FrontRight")
    bumper_left  = subdevice.Bumper(dcm, mem, "FrontLeft")
    bumper_back  = subdevice.Bumper(dcm, mem, "Back")

    list_bumpers = [bumper_right, bumper_left, bumper_back]

    file_extension = "csv"
    robot_name = system.robotName()
    date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_type = "wheels_speeds_when_bumper_pressions"
    file_name = "-".join([robot_name, date, log_type])
    output = ".".join([file_name, file_extension])

    data = open(output, 'w')
    data.write("Bumper FR" + "," +
               "Bumper FL" + "," +
               "Bumper B" + "," +
               "wheel FR speed [rad/s]" + "," +
               "wheel FL speed [rad/s]" + "," +
               "Wheel B speed [rad/s]" + "\n")
    data.flush()

    threading_flag = threading.Event()

    def log(threading_flag):
        while not threading_flag.is_set():
            line = ""
            flag = 0
            speed_fr = wheel_fr_speed_sensor.value
            speed_fl = wheel_fl_speed_sensor.value
            speed_b  = wheel_b_speed_sensor.value
            for bumper in list_bumpers:
                if bumper.value == 1:
                    flag += 1
                    line += str(1) + ","
                else:
                    line += str(0) + ","
            if flag > 0:
                line += str(speed_fr) + "," + \
                        str(speed_fl) + "," + \
                        str(speed_b) + "\n"
                data.write(line)
                data.flush()
            qha_tools.wait(dcm, wait_time_bumpers)

    log_thread = threading.Thread(target=log, args=(threading_flag,))
    log_thread.start()

    def fin():
        threading_flag.set()

    request.addfinalizer(fin)
