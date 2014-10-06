import pytest
import tools
import subdevice
import time
import threading
import os
import csv


@pytest.fixture(scope="module")
def test_time():
    """
    Returns the test time [ms]
    """
    return int(tools.read_parameter("config.cfg", "Parameters", "TestTime"))


@pytest.fixture(scope="session")
def stop_robot(request, dcm, mem):
    """
    Stops properly the robot
    """
    def fin():
        print "robot is stopped"
        wheel_fr_speed_actuator = subdevice.WheelSpeedActuator(
            dcm, mem,"wheelFR")
        wheel_fl_speed_actuator = subdevice.WheelSpeedActuator(
            dcm, mem,"wheelFL")
        wheel_b_speed_actuator  = subdevice.WheelSpeedActuator(
            dcm, mem,"WheelB")
        wheel_fr_speed_actuator.qvalue = (0.0, 0)
        wheel_fl_speed_actuator.qvalue = (0.0, 0)
        wheel_b_speed_actuator.qvalue  = (0.0, 0)
        tools.wait(dcm, 2000)

    request.addfinalizer(fin)


@pytest.fixture(scope="session")
def unstiff_joints(dcm, mem):
    """
    Unstiff all joints except HipPitch, KneePitch and wheels
    """
    joints = tools.use_section("config.cfg", "JulietteJoints")
    for joint in joints:
        joint_hardness = subdevice.JointHardnessActuator(dcm, mem, joint)
        joint_hardness.qqvalue = 0.0
    tools.wait(dcm, 1000)


@pytest.fixture(scope="session")
def log_wheels_speed(request, dcm, mem):
    """
    Log wheels' speeds [rad/s] every 0.5s
    """
    wheel_fr = subdevice.WheelSpeedSensor(dcm, mem,"wheelFR")
    wheel_fl = subdevice.WheelSpeedSensor(dcm, mem,"wheelFL")
    wheel_b  = subdevice.WheelSpeedSensor(dcm, mem,"WheelB")

    log_file = open("wheels_speeds.csv", 'w')
    log_file.write(
            "Time (s)" + "," +
            "wheel_fr speed (rad/s)" + "," +
            "wheel_fl speed (rad/s)" + "," +
            "WheelB speed (rad/s)" + "\n"
    )

    threading_flag = threading.Event()

    def log(threading_flag):
        cpt = 1
        time_init = time.time()
        while not threading_flag.is_set():
            line = ""
            if float(format((time.time() - time_init), '.1f')) == (cpt * 0.5):
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
def log_bumper_pressions(request, dcm, mem):
    """
    If one or more bumpers are pressed,
    it returns True and saves wheels' speeds (rad/s)
    """
    wheel_fr = subdevice.WheelSpeedSensor(
        dcm, mem,"wheel_fr")
    wheel_fl = subdevice.WheelSpeedSensor(
        dcm, mem,"wheel_fl")
    wheel_b  = subdevice.WheelSpeedSensor(
        dcm, mem,"WheelB")

    bumper_right = subdevice.Bumper(dcm, mem, "FrontRight")
    bumper_left  = subdevice.Bumper(dcm, mem, "FrontLeft")
    bumper_back  = subdevice.Bumper(dcm, mem, "Back")

    list_bumpers = [bumper_right, bumper_left, bumper_back]

    data = open("test_bumper.csv", 'w')
    data.write("Bumper FR" + "," +
               "Bumper FL" + "," +
               "Bumper B" + "," +
               "wheel_fr speed (rad/s)" + "," +
               "wheel_fl speed (rad/s)" + "," +
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
            tools.wait(dcm, 100)

    log_thread = threading.Thread(target=log, args=(threading_flag,))
    log_thread.start()

    def fin():
        threading_flag.set()

    request.addfinalizer(fin)
