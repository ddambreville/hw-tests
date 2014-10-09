import pytest
import tools
import subdevice
import threading
import time
import os
import csv


@pytest.fixture(scope="session")
def wait_time():
    """
    Returns a wait time [ms]
    """
    return int(tools.read_parameter("config.cfg", "MobileBaseParameters",
                                    "wait_time"))


@pytest.fixture(scope="session")
def wait_time_bumpers():
    """
    Returns the wait time before checking again bumpers [ms]
    """
    return int(tools.read_parameter("config.cfg", "MobileBaseParameters",
                                    "wait_time_bumpers"))


@pytest.fixture(scope="session")
def log_period():
    """
    Returns the log period [s]
    """
    return float(tools.read_parameter("config.cfg", "MobileBaseParameters",
                                      "log_period"))


@pytest.fixture(scope="session")
def min_fraction():
    """
    Returns the minimum fraction speed for a wheel
    """
    return float(tools.read_parameter("config.cfg", "MobileBaseParameters",
                                      "min_fraction"))


@pytest.fixture(scope="session")
def max_fraction():
    """
    Returns the maximum fraction speed for a wheel
    """
    return float(tools.read_parameter("config.cfg", "MobileBaseParameters",
                                      "max_fraction"))


@pytest.fixture(scope="session")
def max_random():
    """
    Returns the maximum value for rand funtion
    """
    return int(tools.read_parameter("config.cfg", "MobileBaseParameters",
                                    "max_random"))

@pytest.fixture(scope="session")
def nb_cables_crossing():
    """
    Returns wanted number of cables crossing 
    """
    return int(tools.read_parameter("config.cfg", "CablesRoutingParameters",
                                    "Nb_cables_crossing"))


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

        tools.wait(dcm, wait_time)

    request.addfinalizer(fin)


@pytest.fixture(scope="session")
def unstiff_joints(dcm, mem, wait_time):
    """
    Unstiff all joints except HipPitch, KneePitch and Wheels
    """
    joints = tools.use_section("config.cfg", "JulietteJoints")
    for joint in joints:
        joint_hardness = subdevice.JointHardnessActuator(dcm, mem, joint)
        joint_hardness.qqvalue = 0.0
    tools.wait(dcm, wait_time)


@pytest.fixture(scope="session")
def log_wheels_speed(request, dcm, mem, log_period):
    """
    Log wheels' speeds [rad/s] every 0.5s
    """
    wheel_fr_speed_sensor = subdevice.WheelSpeedSensor(
        dcm, mem, "WheelFR")
    wheel_fl_speed_sensor = subdevice.WheelSpeedSensor(
        dcm, mem, "WheelFL")
    wheel_b_speed_sensor  = subdevice.WheelSpeedSensor(
        dcm, mem, "WheelB")

    log_file = open("wheels_speeds.csv", 'w')
    log_file.write(
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
                log_file.write(line)

    log_thread = threading.Thread(target=log, args=(threading_flag,))
    log_thread.start()

    print("log_wheels_speeds started !\n")

    def fin():
        threading_flag.set()

    request.addfinalizer(fin)


@pytest.fixture(scope="session")
def log_bumper_pressions(request, dcm, mem, wait_time_bumpers):
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

    data = open("bumper_pressions.csv", 'w')
    data.write("Bumper FR" + "," +
               "Bumper FL" + "," +
               "Bumper B" + "," +
               "wheel FR speed [rad/s]" + "," +
               "wheel FL speed [rad/s]" + "," +
               "Wheel B speed [rad/s]" + "\n")

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
                line += str(speed_fr) + "," +\
                        str(speed_fl) + "," +\
                        str(speed_b) + "\n"
                data.write(line)
            tools.wait(dcm, wait_time_bumpers)

    log_thread = threading.Thread(target=log, args=(threading_flag,))
    log_thread.start()

    print("log_bumper_pressions started !\n")

    def fin():
        threading_flag.set()

    request.addfinalizer(fin)
