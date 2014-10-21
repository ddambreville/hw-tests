import pytest
import qha_tools
import subdevice


@pytest.fixture(params=qha_tools.use_section("temperature_protection.cfg", "JulietteJoints"))
def test_objects_dico(request, dcm, mem):
    """
    Create the appropriate objects for each joint.
    """
    joint_position_actuator = subdevice.JointPositionActuator(
        dcm, mem, request.param)
    joint_position_sensor = subdevice.JointPositionSensor(
        dcm, mem, request.param)
    joint_temperature_sensor = subdevice.JointTemperature(
        dcm, mem, request.param)
    joint_current_sensor = subdevice.JointCurrentSensor(
        dcm, mem, request.param)
    joint_hardness_actuator = subdevice.JointHardnessActuator(
        dcm, mem, request.param)

    # creating a dictionnary with all the objects
    dico_object = {
        "jointPositionActuator": joint_position_actuator,
        "jointPositionSensor": joint_position_sensor,
        "jointTemperatureSensor": joint_temperature_sensor,
        "jointCurrentSensor": joint_current_sensor,
        "JointHardnessActuator": joint_hardness_actuator
    }
    return dico_object


@pytest.fixture(scope="module")
def parameters():
    """It returns the test parameters"""
    test_time = int(qha_tools.read_parameter(
        "temperature_protection.cfg", "Parameters", "TestTime"))
    test_time_limit = int(qha_tools.read_parameter(
        "temperature_protection.cfg", "Parameters", "TestTimeLimit"))
    limit_extension = int(qha_tools.read_parameter(
        "temperature_protection.cfg", "Parameters", "LimitExtension"))
    sa_nb_points = int(qha_tools.read_parameter(
        "temperature_protection.cfg", "Parameters", "SlidingAverageNbPoints"))
    limit_factor = float(qha_tools.read_parameter(
        "temperature_protection.cfg", "Parameters", "LimitFactor"))

    dico_to_return = {
        "test_time": test_time,
        "test_time_limit": test_time_limit,
        "limit_extension": limit_extension,
        "sa_nb_points": sa_nb_points,
        "limit_factor": limit_factor
    }
    return dico_to_return
