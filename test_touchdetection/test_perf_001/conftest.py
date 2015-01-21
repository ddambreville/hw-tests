import pytest
import subdevice
import qha_tools
from naoqi import ALProxy


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


@pytest.fixture(params=qha_tools.use_section("perf_001.cfg", "Joints"))
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
    joint_hardness = subdevice.JointHardnessActuator(dcm, mem, request.param)

    dico_objects = {
        "jointName": str(request.param),
        "jointPositionActuator": joint_position_actuator,
        "jointPositionSensor": joint_position_sensor,
        "jointSpeedActuator": joint_speed_actuator,
        "jointSpeedSensor": joint_speed_sensor,
        "jointTemperature": joint_temperature,
        "jointHardness": joint_hardness
    }
    return dico_objects


@pytest.fixture(params=qha_tools.use_section("perf_001.cfg", "Direction"))
def direction(request):
    """
    Direction
    """
    return str(request.param)


@pytest.fixture(scope="session")
def parameters():
    return qha_tools.read_section("perf_001.cfg", "TestParameters")


@pytest.fixture(params=qha_tools.use_section("perf_001.cfg", "Speed"))
def speed(request):
    """
    Speed
    """
    return float(request.param)


@pytest.fixture(scope="session")
def remove_sensors(alnavigation):
    """
    Fixture which remove base sensors.
    """
    alnavigation._removeSensor("Laser")
    alnavigation._removeSensor("Sonar")
    alnavigation._removeSensor("Asus")


@pytest.fixture(scope="session")
def alnavigation(robot_ip, port):
    """Fixture which returns a proxy to ALNavigation module."""
    return ALProxy("ALNavigation", robot_ip, port)


@pytest.fixture(scope="session")
def alleds(robot_ip, port):
    """ Fixture which returns a proxy to ALLeds module."""
    return ALProxy("ALLeds", robot_ip, port)
