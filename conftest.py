from naoqi import ALProxy
import tools
import time
import subdevice
import pytest


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
def motion(robot_ip, port):
    """Try to make a proxy to ALMotion."""
    try:
        return ALProxy("ALMotion", robot_ip, port)
    except RuntimeError:
        return "MotionKilled"


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

    return tools.read_parameter(
        "../../global_test_configuration/parameters.cfg",
        "General",
        "ResultsFolder") + "/" + result_folder_name


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
def wake_up(request, motion):
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
