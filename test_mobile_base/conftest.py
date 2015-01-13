import pytest
import tools
import subdevice
import threading
import time
import datetime
import os
import csv
from naoqi import ALProxy
from subdevice import InertialSensorBase
import ConfigParser


@pytest.fixture(scope="session")
def leds(robot_ip, port):
    """
    Fixture which returns a proxy to ALLeds module
    """
    return ALProxy("ALLeds", robot_ip, port)


@pytest.fixture(scope="session")
def expressiveness(robot_ip, port):
    """
    Fixture which returns a proxy to ALExpressiveness module
    """
    return ALProxy("_ALExpressiveness", robot_ip, port)


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
    Returns the time before checking bumpers again [ms]
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
    Returns the maximum value for the rand funtion
    """
    return int(tools.read_parameter("config.cfg", "MobileBaseParameters",
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

@pytest.fixture(scope='session')
def log_wheels_actu_sens(request, dcm, mem, system, log_period):
    """
    Log wheels' speeds [rad/s] every 0.5s
    """
    wheel_fr_speed_sensor = subdevice.WheelSpeedSensor(
        dcm, mem, "WheelFR")
    wheel_fl_speed_sensor = subdevice.WheelSpeedSensor(
        dcm, mem, "WheelFL")
    wheel_b_speed_sensor  = subdevice.WheelSpeedSensor(
        dcm, mem, "WheelB")
    wheel_fr_speed_actuator = subdevice.WheelSpeedActuator(
        dcm, mem, "WheelFR")
    wheel_fl_speed_actuator = subdevice.WheelSpeedActuator(
        dcm, mem, "WheelFL")
    wheel_b_speed_actuator  = subdevice.WheelSpeedActuator(
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
            "wheel FR speed sensor [rad/s]" + "," +
            "wheel FR speed actuator [rad/s]" + "," +
            "wheel FL speed sensor [rad/s]" + "," +
            "wheel FL speed actuator [rad/s]" + "," +
            "Wheel B speed sensor [rad/s]" + "," + 
            "Wheel B speed actuator [rad/s]" + "\n"
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
                        str(wheel_fr_speed_actuator.value) + "," + \
                        str(wheel_fl_speed_sensor.value) + "," + \
                        str(wheel_fl_speed_actuator.value) + "," + \
                        str(wheel_b_speed_sensor.value) + "," + \
                        str(wheel_b_speed_actuator.value) + "\n"
                data.write(line)
                data.flush()

    log_thread = threading.Thread(target=log, args=(threading_flag,))
    log_thread.start()

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
            tools.wait(dcm, wait_time_bumpers)

    log_thread = threading.Thread(target=log, args=(threading_flag,))
    log_thread.start()

    def fin():
        threading_flag.set()

    request.addfinalizer(fin)
PATH = os.path.dirname(os.path.abspath(__file__))

@pytest.fixture(scope="session")
def robot_ip(request):
    """Robot IP adress."""
    return request.config.getoption("--ip")


@pytest.fixture(scope="session")
def port(request):
    """Returns port."""
    return request.config.getoption("--port")
@pytest.fixture(scope="session")
def mem(robot_ip, port):
    """Fixture which returns a proxy to ALMemory module."""
    return ALProxy("ALMemory", robot_ip, port)

@pytest.fixture(scope="session")
def mem(robot_ip, port):
    """Fixture which returns a proxy to ALMemory module."""
    return ALProxy("ALMemory", robot_ip, port)


@pytest.fixture(scope="session")
def motion(robot_ip, port):
    """Try to make a proxy to ALMotion."""
    try:
        return ALProxy("ALMotion", robot_ip, port)
    except RuntimeError:
        return "MotionKilled"

@pytest.fixture(scope="session")
def alrecharge(robot_ip, port):
    """ Fixture chich returns a proxy to ALRecharge module. """
    return ALProxy("ALRecharge", robot_ip, port)


@pytest.fixture(scope="session")
def robot_posture(robot_ip, port):
    """Fixture which returns a proxy to ALRobotPosture module."""
    return ALProxy("ALRobotPosture", robot_ip, port)


@pytest.fixture(scope="session", autouse=False)
def kill_motion(motion):
    """
    Fixture which kills ALMotion module.
    It allows to use DCM module without conflict.
    """
    try:
        motion.exit()
    except:
        pass


@pytest.fixture(scope="session")
def dcm(robot_ip, port):
    """Proxy to DCM module."""
    return ALProxy("DCM", robot_ip, port)
@pytest.fixture(scope="session")
def autonomous_life(robot_ip, port):
    """Fixture which returns a proxy to ALAutonomousLife module."""
    return ALProxy("ALAutonomousLife", robot_ip, port)


@pytest.fixture(scope="session")
def behavior_manager(robot_ip, port):
    """Proxy to ALBehaviorManager module."""
    return ALProxy("ALBehaviorManager", robot_ip, port)


@pytest.fixture(scope="session")
def system(robot_ip, port):
    """Proxy to ALSystem module."""
    return ALProxy("ALSystem", robot_ip, port)


@pytest.fixture(scope="session")
def robot(system):
    """Fixture which gives robot name."""
    return system.robotName()


@pytest.fixture(scope="session")
def wake_up_pos():
    """
    Fixture which retrieves wakeUp joints position from a configuration file.
    """
    return tools.read_section("juliette_positions.cfg", "wakeUp")


@pytest.fixture(scope="session")
def rest_pos():
    """
    Fixture which retrieves rest joints position from a configuration file.
    """
    return tools.read_section(PATH + "/global_test_configuration/"
                              "juliette_positions.cfg", "rest")


@pytest.fixture(scope="session")
def zero_pos():
    """
    Fixture which retrieves zero joints position from a configuration file.
    """
    return tools.read_section(PATH + "/global_test_configuration/"
                              "juliette_positions.cfg", "zero")


@pytest.fixture(scope="session")
def stiff_robot(request, dcm, mem, rest_pos):
    """
    This method automatically stiffs the robot at the beginning of the
    tests. Once all the tests have been done, the robot goes to rest position
    and stiffness is set to 0.
    """
    list_hardness = mem.getDataList("Hardness/Actuator/Value")
    dcm.createAlias(["Hardness", list_hardness])
    dcm.set(["Hardness", "Merge", [[1.0, dcm.getTime(0)]]])

    def fin():
        """Method automatically executed at the end of the test."""
        dcm.set(["Hardness", "Merge", [[1.0, dcm.getTime(0)]]])
        subdevice.multiple_set(dcm, mem, rest_pos, wait=True)
        dcm.set(["Hardness", "Merge", [[0.1, dcm.getTime(0)]]])
        dcm.set(["Hardness", "Merge", [[0., dcm.getTime(1000)]]])

    request.addfinalizer(fin)


@pytest.fixture(scope="session")
def stiff_robot_wheels(request, dcm, mem):
    """
    This method automatically stiffs the robot wheels at the beginning of the
    tests. Once all the tests have been done, the robot goes to rest position
    and stiffness is set to 0.
    """
    list_hardness = mem.getDataList("Stiffness/Actuator/Value")
    dcm.createAlias(["WheelsHardness", list_hardness])
    dcm.set(["WheelsHardness", "Merge", [[1.0, dcm.getTime(0)]]])

    def fin():
        """Method automatically executed at the end of the test."""
        dcm.set(["WheelsHardness", "Merge", [[0.1, dcm.getTime(0)]]])
        dcm.set(["WheelsHardness", "Merge", [[0., dcm.getTime(1000)]]])

    request.addfinalizer(fin)


@pytest.fixture(scope="session")
def result_base_folder(system, mem):
    """
    Fixture which returns the result base folder, where we want to
    store the log files.
    """
    local_time = time.localtime(time.time())
    year = tools.int_to_two_digit_string(local_time[0])
    month = tools.int_to_two_digit_string(local_time[1])
    day = tools.int_to_two_digit_string(local_time[2])
    hour = tools.int_to_two_digit_string(local_time[3])
    minu = tools.int_to_two_digit_string(local_time[4])
    sec = tools.int_to_two_digit_string(local_time[5])

    result_folder_name = "{HeadType}_{HeadID}_{SystemVersion}_{Year}_{Month}_{Day}_{Hour}:{Min}:{Sec}".format(
        HeadType=mem.getData("RobotConfig/Head/Type"),
        HeadID=mem.getData("RobotConfig/Head/HeadId"),
        SystemVersion=system.systemVersion(),
        Year=year,
        Month=month,
        Day=day,
        Hour=hour,
        Min=minu,
        Sec=sec
    )

    return "Results" + "/" + result_folder_name


@pytest.fixture(scope="session")
def disable_push_recovery(request, motion):
    """
    For tests using naoqi ALMotion module.
    Disables push recovery and enables it at the end on the test session.
    """
    print "disabling push recovery..."
    motion.setPushRecoveryEnabled(False)

    def fin():
        """tear down."""
        print "enabling push recovery..."
        motion.setPushRecoveryEnabled(True)
    request.addfinalizer(fin)


@pytest.fixture(scope="session")
def disable_arms_external_collisions(request, motion):
    """
    Only for tests using naoqi ALMotion module.
    Disables arms external collisions and enables it at the end on the test
    session.
    """
    print "disabling arms external collision..."
    motion.setExternalCollisionProtectionEnabled('Arms', False)

    def fin():
        """tear down."""
        print "enabling arms external collision..."
        motion.setExternalCollisionProtectionEnabled('Arms', True)
    request.addfinalizer(fin)


@pytest.fixture(scope="session")
def disable_fall_manager(request, motion):
    """
    Only for tests using naoqi ALMotion module.
    Disables fall manager and enables it at the end on the test session.
    """
    print "disabling fall manager..."
    motion.setExternalCollisionProtectionEnabled('Arms', False)

    def fin():
        """tear down."""
        print "enabling fall manager..."
        motion.setExternalCollisionProtectionEnabled('Arms', True)
    request.addfinalizer(fin)


@pytest.fixture(scope="session")
def wake_up_rest(request, motion):
    """
    Robot wake up
    """
    print "robot waking up..."
    motion.wakeUp()

    def fin():
        """tear down."""
        print "\nrobot automatically going to rest position..."
        motion.rest()
    request.addfinalizer(fin)


@pytest.fixture(scope="session")
def wakeup_no_rotation(request, motion):
    """
    Make the robot wakeUp at the beginning
    of the test (without rotation due to the Active Diagnosis)
    and go to rest at the end
    """
    # Remove the rotation due to the Active Diagnosis
    motion.setMotionConfig([["ENABLE_MOVE_API", False]])
    motion.wakeUp()
    motion.setMotionConfig([["ENABLE_MOVE_API", True]])

    def fin():
        """Method automatically executed at the end of the test"""
        motion.rest()
    request.addfinalizer(fin)


@pytest.fixture(scope="session")
def remove_safety(request, motion):
    """
    Fixture which remove the robot safety
    """
    motion.setExternalCollisionProtectionEnabled("All", 0)

    def fin():
        """tear down."""
        motion.setExternalCollisionProtectionEnabled("All", 0)
    request.addfinalizer(fin)


@pytest.fixture(scope="session")
def remove_diagnosis(request, motion):
    """
    Fixture which remove the robot diagnosis
    """
    motion.setDiagnosisEffectEnabled(0)

    def fin():
        """tear down."""
        motion.setDiagnosisEffectEnabled(0)
    request.addfinalizer(fin)


@pytest.fixture(scope="session")
def active_all_laser(dcm):
    """
    Turn on all the lasers
    """
    dcm.set(
        ["Device/SubDeviceList/Platform/LaserSensor/"
         "Front/Reg/OperationMode/Actuator/Value",
         "ClearAll", [[7.0, dcm.getTime(0)]]])


@pytest.fixture(scope="session")
def wake_up_pos_brakes_closed(request, dcm, mem, wake_up_pos, rest_pos,
                              kill_motion, stiff_robot):
    """
    Fixture which make the robot wakeUp, close brakes.
    Control if brakes slip.
    """

    subdevice.multiple_set(dcm, mem, wake_up_pos, wait=True)
    thread_flag = threading.Event()

    def control():
        """ Control if brakes slip"""
        kneepitch_position_actuator = subdevice.JointPositionActuator(
            dcm, mem, "KneePitch")
        kneepitch_position_sensor = subdevice.JointPositionSensor(
            dcm, mem, "KneePitch")
        kneepitch_hardness_actuator = subdevice.JointHardnessActuator(
            dcm, mem, "KneePitch")
        hippitch_position_actuator = subdevice.JointPositionActuator(
            dcm, mem, "HipPitch")
        hippitch_position_sensor = subdevice.JointPositionSensor(
            dcm, mem, "HipPitch")
        hippitch_hardness_actuator = subdevice.JointHardnessActuator(
            dcm, mem, "HipPitch")

        hippitch_hardness_actuator.qqvalue = 0.
        kneepitch_hardness_actuator.qqvalue = 0.

        while not thread_flag.is_set():
            if abs(hippitch_position_sensor.value) > 0.1 or\
                    abs(kneepitch_position_sensor.value) > 0.1:
                hippitch_hardness_actuator.qqvalue = 1.
                kneepitch_hardness_actuator.qqvalue = 1.
                hippitch_position_actuator.qvalue = (0., 1000)
                kneepitch_position_actuator.qvalue = (0., 1000)
                tools.wait(dcm, 2100)
                hippitch_hardness_actuator.qqvalue = 0.
                kneepitch_hardness_actuator.qqvalue = 0.


    my_thread = threading.Thread(target=control)
    my_thread.start()

    def fin():
        """
        Stop control and put the robot in rest position at the end of session"
        """
        thread_flag.set()
        subdevice.multiple_set(dcm, mem, rest_pos, wait=True)

    request.addfinalizer(fin)
@pytest.fixture(scope="module")
def get_accelerometer_objects(request, result_base_folder, dcm, mem):
    """
    Return a dictionary with several objects for
    each accelerometer of the inertial base
    """
    dico = {}
    dico["Acc_x"] = InertialSensorBase(
        dcm, mem, "AccelerometerX")
    dico["Acc_y"] = InertialSensorBase(
        dcm, mem, "AccelerometerY")
    dico["Acc_z"] = InertialSensorBase(
        dcm, mem, "AccelerometerZ")
    logger = tools.Logger()
    dico["logger"] = logger

    def fin():
        """Method executed after a joint test."""
        result_file_path = "/".join(
            [
                result_base_folder,
                "Accelerometer_Log"
            ]) + ".csv"
        logger.log_file_write(result_file_path)

    request.addfinalizer(fin)
    return dico


@pytest.fixture(scope="module")
def get_all_inertialbase_objects(request, result_base_folder, dcm, mem):
    """
    Return a dictionary with several objects for
    each sensor value of the inertial base
    """
    dico = {}
    coord = ["X", "Y", "Z"]
    for each in coord:
        dico["Acc" + each] = InertialSensorBase(
            dcm, mem, "Accelerometer" + each)
        dico["Angle" + each] = InertialSensorBase(
            dcm, mem, "Angle" + each)
        dico["Gyr" + each] = InertialSensorBase(
            dcm, mem, "Gyr" + each)
    logger = tools.Logger()
    dico["logger"] = logger

    def fin():
        """Method executed after a joint test."""
        result_file_path = "/".join(
            [
                result_base_folder,
                "InertialBase_Log"
            ]) + ".csv"
        logger.log_file_write(result_file_path)

    request.addfinalizer(fin)
    return dico