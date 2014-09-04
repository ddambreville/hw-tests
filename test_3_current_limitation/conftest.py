import pytest
import tools
import subdevice


@pytest.fixture(params=tools.use_section("test_current_limitation.cfg", "JulietteJoints"))
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

    # creating a dictionnary with all the objects
    dico_object = {
        "jointPositionActuator": joint_position_actuator,
        "jointPositionSensor": joint_position_sensor,
        "jointTemperatureSensor": joint_temperature_sensor,
        "jointCurrentSensor": joint_current_sensor
    }
    return dico_object


@pytest.fixture(scope="module")
def parameters():
    """It returns the test parameters"""
    test_time = int(tools.read_parameter(
        "test_current_limitation.cfg", "Parameters", "TestTime"))
    test_time_limit = int(tools.read_parameter(
        "test_current_limitation.cfg", "Parameters", "TestTimeLimit"))
    limit_extension = int(tools.read_parameter(
        "test_current_limitation.cfg", "Parameters", "LimitExtension"))
    limit_factor = float(tools.read_parameter(
        "test_current_limitation.cfg", "Parameters", "LimitFactor"))
    sa_nb_points = int(tools.read_parameter(
        "test_current_limitation.cfg", "Parameters", "SlidingAverageNbPoints"))
    dico_to_return = {
        "test_time": test_time,
        "test_time_limit": test_time_limit,
        "limit_extension": limit_extension,
        "limit_factor": limit_factor,
        "sa_nb_points": sa_nb_points
    }
    return dico_to_return
