import pytest
import tools
import subdevice
import time
import threading

@pytest.fixture(scope="module")
def test_time():
    """
    Returns the test time [ms]
    """
    return int(tools.read_parameter("config.cfg", "Parameters", "TestTime"))


@pytest.fixture(scope="module")
def nb_cycles():
    """
    Returns the number of cycles
    """
    return int(tools.read_parameter("config.cfg", "Parameters", "NbCycles"))


@pytest.fixture(scope="session")
def stop_robot(request, dcm, mem):
    """
    Stops properly the robot
    """
    def fin():
        print "robot is stopped"
        wheelfr_speed_actuator = subdevice.WheelSpeedActuator(dcm, mem,"WheelFR")
        wheelfl_speed_actuator = subdevice.WheelSpeedActuator(dcm, mem,"WheelFL")
        wheelb_speed_actuator  = subdevice.WheelSpeedActuator(dcm, mem,"WheelB")
        wheelfr_speed_actuator.qvalue = (0.0, 0)
        wheelfl_speed_actuator.qvalue = (0.0, 0)
        wheelb_speed_actuator.qvalue  = (0.0, 0)
        tools.wait(dcm, 2000)
        
    request.addfinalizer(fin)


@pytest.fixture(scope="session")
def wakeUp(dcm, mem, wake_up_pos):
    """
    Wakes up the robot
    """
    subdevice.multiple_set(dcm, mem, wake_up_pos, wait=True)


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
    wheelFR = subdevice.WheelSpeedSensor(dcm, mem,"WheelFR")
    wheelFL = subdevice.WheelSpeedSensor(dcm, mem,"WheelFL")
    wheelB  = subdevice.WheelSpeedSensor(dcm, mem,"WheelB")

    log_file = open("wheels_speeds.csv", 'w')
    log_file.write(
            "Time (s)" + "," +
            "WheelFR speed (rad/s)" + "," +
            "WheelFL speed (rad/s)" + "," +
            "WheelB speed (rad/s)" + "\n"
    )

    threading_flag = threading.Event()

    def log(threading_flag):
        cpt = 1
        t0 = time.time()
        while not threading_flag.is_set():
            line = ""
            if float(format((time.time() - t0), '.1f')) == (cpt * 0.5):
                cpt += 1
                line += str(float(format((time.time() - t0), '.1f'))) + "," + \
                        str(wheelFR.value) + "," + \
                        str(wheelFL.value) + "," + \
                        str(wheelB.value) + "\n"
                log_file.write(line)

    log_thread = threading.Thread(target=log, args=(threading_flag,))
    log_thread.start()

    def fin():
        threading_flag.set()

    request.addfinalizer(fin)
    

@pytest.fixture(scope="session")
def log_bumper_pressions(request, dcm, mem, test_time):
    """
    If one or more bumpers are pressed,
    it returns True and saves wheels' speeds (rad/s)
    """
    wheelFR = subdevice.WheelSpeedSensor(dcm, mem,"WheelFR")
    wheelFL = subdevice.WheelSpeedSensor(dcm, mem,"WheelFL")
    wheelB  = subdevice.WheelSpeedSensor(dcm, mem,"WheelB")

    bumper_right = subdevice.Bumper(dcm, mem, "FrontRight")
    bumper_left  = subdevice.Bumper(dcm, mem, "FrontLeft")
    bumper_back  = subdevice.Bumper(dcm, mem, "Back")

    list_bumpers = [bumper_right, bumper_left, bumper_back]

    data = open("test_bumper.csv", 'w')
    data.write("Bumper FR" + "," +
               "Bumper FL" + "," +
               "Bumper B" + "," +
               "WheelFR speed (rad/s)" + "," +
               "WheelFL speed (rad/s)" + "," +
               "WheelB speed (rad/s)" + "\n")

    threading_flag = threading.Event()

    def log(threading_flag):
        while not threading_flag.is_set():
            line = ""
            flag = 0
            speedFR = wheelFR.value
            speedFL = wheelFL.value
            speedB  = wheelB.value
            for bumper in list_bumpers:
                if bumper.value == 1:
                    flag += 1
                    line += str(1) + ","
                else:
                    line += str(0) + ","
            if flag > 0:
                line += str(speedFR) + "," +\
                        str(speedFL) + "," +\
                        str(speedB) + "\n"
                data.write(line)
            tools.wait(dcm, 100)

    log_thread = threading.Thread(target=log, args=(threading_flag,))
    log_thread.start()

    def fin():
        threading_flag.set()

    request.addfinalizer(fin)

