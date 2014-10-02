from naoqi import ALProxy
import tools
import time
import subdevice
import pytest
import threading


def pytest_addoption(parser):
    """Configuration of pytest parsing."""
    parser.addoption(
        "--ip",
        action="store",
        default="127.0.0.1",
        help="Robot IP"
    )
    parser.addoption(
        "--port",
        action="store",
        default=9559,
        help="Robot port"
    )
    parser.addoption(
        "--plot",
        action="store",
        default=False,
        help="Choose True if you want real time plot."
    )

    parser.addoption('--repeat', action='store',
                     help='Number of times to repeat each test')


def pytest_generate_tests(metafunc):
    if metafunc.config.option.repeat is not None:
        count = int(metafunc.config.option.repeat)

        # We're going to duplicate these tests by parametrizing them,
        # which requires that each test has a fixture to accept the parameter.
        # We can add a new fixture like so:
        metafunc.fixturenames.append('tmp_ct')

        # Now we parametrize. This is what happens when we do e.g.,
        # @pytest.mark.parametrize('tmp_ct', range(count))
        # def test_foo(): pass
        metafunc.parametrize('tmp_ct', range(count))


@pytest.fixture(scope="session")
def robot_ip(request):
    """Robot IP adress."""
    return request.config.getoption("--ip")


@pytest.fixture(scope="session")
def port(request):
    """Returns port."""
    return request.config.getoption("--port")


@pytest.fixture(scope="session")
def plot(request):
    """Enable real time plot."""
    return request.config.getoption("--plot")


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
def leds(robot_ip, port):
    """Fixture which returns a proxy to ALLeds module."""
    return ALProxy("ALLeds", robot_ip, port)


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
    return tools.read_section("../global_test_configuration/juliette_positions.cfg", "wakeUp")


@pytest.fixture(scope="session")
def rest_pos():
    """
    Fixture which retrieves rest joints position from a configuration file.
    """
    return tools.read_section("../global_test_configuration/juliette_positions.cfg", "rest")


@pytest.fixture(scope="session")
def zero_pos():
    """
    Fixture which retrieves zero joints position from a configuration file.
    """
    return tools.read_section("../global_test_configuration/juliette_positions.cfg", "zero")


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
        ["Device/SubDeviceList/Platform/LaserSensor/Front/Reg/OperationMode/Actuator/Value",
         "ClearAll", [[7.0, dcm.getTime(0)]]])


@pytest.fixture(scope="session")
def wake_up_pos_brakes_closed(request, dcm, mem, wake_up_pos,rest_pos,
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
                print "Slip"
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
