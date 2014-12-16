import pytest
import qha_tools
import subdevice


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


@pytest.fixture(params=qha_tools.use_section("touch_detection.cfg", "Speed"))
def speed_value(request):
    """
    Speed
    """
    dico_speed = {
        "Speed": float(request.param)
    }
    return dico_speed


@pytest.fixture(scope="session")
def parameters():
    return qha_tools.read_section("touch_detection.cfg", "TestParameters")
