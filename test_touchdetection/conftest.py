import pytest
import qha_tools
import subdevice
from naoqi import ALProxy
from naoqi import ALBroker
from qi import Session


class MotionActuatorValue(object):

    def __init__(self, mem, name):
        self.mem = mem
        self.name = name

    def _get_value(self):
        """ Get value from ALMemory. """
        return float(self.mem.getData("Motion/Velocity/Command/" + self.name))

    value = property(_get_value)


class MotionSensorValue(object):

    def __init__(self, mem, name):
        self.mem = mem
        self.name = name

    def _get_value(self):
        """ Get value from ALMemory. """
        return float(self.mem.getData("Motion/Velocity/Sensor/" + self.name))

    value = property(_get_value)


@pytest.fixture(scope="session")
def broker(robot_ip, port):
    """
    broker
    """
    return ALBroker("broker", "0.0.0.0", 0, robot_ip, port)


@pytest.fixture(scope="session")
def motion_wake_up(request, motion):
    """
    Robot wakeUp.
    """
    motion.wakeUp()

    def fin():
        """Method executed after the end of the test."""
        motion.rest()

    request.addfinalizer(fin)


@pytest.fixture(scope="session")
def remove_safety(request, motion):
    """
    Remove sensors
    """
    motion.setExternalCollisionProtectionEnabled("All", False)

    def fin():
        """Method executed after the end of the test."""
        motion.setExternalCollisionProtectionEnabled("All", True)

    request.addfinalizer(fin)


@pytest.fixture(params=qha_tools.use_section("touch_detection.cfg", "Joints"))
def test_objects_dico(request, dcm, mem):
    """
    Create the appropriate objects for each joint.
    """
    joint_position_actuator = subdevice.JointPositionActuator(
        dcm, mem, request.param)
    joint_position_sensor = subdevice.JointPositionSensor(
        dcm, mem, request.param)
    joint_speed_actuator = MotionActuatorValue(mem, request.param)
    joint_speed_sensor = MotionSensorValue(mem, request.param)
    joint_temperature = subdevice.JointTemperature(dcm, mem, request.param)

    dico_objects = {
        "jointName": str(request.param),
        "jointPositionActuator": joint_position_actuator,
        "jointPositionSensor": joint_position_sensor,
        "jointSpeedActuator": joint_speed_actuator,
        "jointSpeedSensor": joint_speed_sensor,
        "jointTemperature": joint_temperature
    }
    return dico_objects


@pytest.fixture(scope="session")
def parameters():
    return qha_tools.read_section("touch_detection.cfg", "TestParameters")


@pytest.fixture(scope="function", autouse=False)
def session(robot_ip, port, request):
    """ Connect a session to a NAOqi """
    ses = Session()
    ses.connect("tcp://" + robot_ip + ":" + str(port))
    return ses
