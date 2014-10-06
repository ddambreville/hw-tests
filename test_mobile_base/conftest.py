import pytest
import tools
import subdevice
import time
import threading
import os
import csv


@pytest.fixture(scope="session")
def test_time():
    """
    Returns the test time [ms]
    """
    return int(tools.read_parameter("config.cfg", "Parameters", "testTime"))


@pytest.fixture(scope="session")
def wait_time():
    """
    Returns a wait time [ms]
    """
    return int(tools.read_parameter("config.cfg", "Parameters", "waitTime"))


@pytest.fixture(scope="session")
def wait_time_bumpers():
    """
    Returns the wait time before checking again bumpers [ms]
    """
    return int(tools.read_parameter("config.cfg", "Parameters", "waitTimeBumpers"))


@pytest.fixture(scope="session")
def log_period():
    """
    Returns the log period [s]
    """
    return int(tools.read_parameter("config.cfg", "Parameters", "logPeriod"))


@pytest.fixture(scope="session")
def min_speed():
    """
    Returns the minimum speed for a wheel [rad/s]
    """
    return int(tools.read_parameter("config.cfg", "Parameters", "minSpeed"))


@pytest.fixture(scope="session")
def max_speed():
    """
    Returns the maximum speed for a wheel [rad/s]
    """
    return int(tools.read_parameter("config.cfg", "Parameters", "maxSpeed"))


@pytest.fixture(scope="session")
def min_random():
    """
    Returns the minimum value for rand funtion
    """
    return int(tools.read_parameter("config.cfg", "Parameters", "minRandom"))


@pytest.fixture(scope="session")
def max_random():
    """
    Returns the maximum value for rand funtion
    """
    return int(tools.read_parameter("config.cfg", "Parameters", "maxRandom"))


@pytest.fixture(scope="session")
def stop_robot(request, dcm, mem, wait_time):
    """
    Stops the robot at the end of the test
    """
    def fin():
        print "Robot stopped"
        wheel_fr_speed_actuator = subdevice.WheelSpeedActuator(
            dcm, mem,"wheelFR")
        wheel_fl_speed_actuator = subdevice.WheelSpeedActuator(
            dcm, mem,"wheelFL")
        wheel_b_speed_actuator  = subdevice.WheelSpeedActuator(
            dcm, mem,"WheelB")
        wheel_fr_speed_actuator.qvalue = (0.0, 0)
        wheel_fl_speed_actuator.qvalue = (0.0, 0)
        wheel_b_speed_actuator.qvalue  = (0.0, 0)
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
    wheel_fr = subdevice.WheelSpeedSensor(dcm, mem,"wheelFR")
    wheel_fl = subdevice.WheelSpeedSensor(dcm, mem,"wheelFL")
    wheel_b  = subdevice.WheelSpeedSensor(dcm, mem,"WheelB")

    log_file = open("wheels_speeds.csv", 'w')
    log_file.write(
            "Time (s)" + "," +
            "wheelFR speed (rad/s)" + "," +
            "wheelFL speed (rad/s)" + "," +
            "WheelB speed (rad/s)" + "\n"
    )

    threading_flag = threading.Event()

    def log(threading_flag):
        cpt = 1
        time_init = time.time()
        while not threading_flag.is_set():
            line = ""
            if float(format((time.time() - time_init), '.1f')) == (cpt * log_period):
                cpt += 1
                line += str(float(format((time.time() - time_init),
                         '.1f'))) + "," + \
                        str(wheel_fr.value) + "," + \
                        str(wheel_fl.value) + "," + \
                        str(wheel_b.value) + "\n"
                log_file.write(line)

    log_thread = threading.Thread(target=log, args=(threading_flag,))
    log_thread.start()

    def fin():
        threading_flag.set()

    request.addfinalizer(fin)


@pytest.fixture(scope="session")
def log_bumper_pressions(request, dcm, mem, wait_time_bumpers):
    """
    If one or more bumpers are pressed,
    it saves wheels' speeds (rad/s)
    """
    wheel_fr = subdevice.WheelSpeedSensor(
        dcm, mem,"wheelFR")
    wheel_fl = subdevice.WheelSpeedSensor(
        dcm, mem,"wheelFL")
    wheel_b  = subdevice.WheelSpeedSensor(
        dcm, mem,"WheelB")

    bumper_right = subdevice.Bumper(dcm, mem, "FrontRight")
    bumper_left  = subdevice.Bumper(dcm, mem, "FrontLeft")
    bumper_back  = subdevice.Bumper(dcm, mem, "Back")

    list_bumpers = [bumper_right, bumper_left, bumper_back]

    data = open("test_bumper.csv", 'w')
    data.write("BumperFR" + "," +
               "BumperFL" + "," +
               "BumperB" + "," +
               "wheelFR speed (rad/s)" + "," +
               "wheelFL speed (rad/s)" + "," +
               "WheelB speed (rad/s)" + "\n")

    threading_flag = threading.Event()

    def log(threading_flag):
        while not threading_flag.is_set():
            line = ""
            flag = 0
            speed_fr = wheel_fr.value
            speed_fl = wheel_fl.value
            speed_b  = wheel_b.value
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

    def fin():
        threading_flag.set()

    request.addfinalizer(fin)
