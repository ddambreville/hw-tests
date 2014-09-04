import pytest
import subdevice
import tools


@pytest.fixture(params=tools.use_section("joint_enslavement.cfg", "JulietteJoints"))
def test_objects_dico(request, result_base_folder, dcm, mem):
    """
    Create the appropriate objects for each joint.
    It logs the informations into a dictionnary and save the data into a file
    after each joint test.
    """
    joint_position_actuator = subdevice.JointPositionActuator(
        dcm, mem, request.param)
    joint_position_sensor = subdevice.JointPositionSensor(
        dcm, mem, request.param)
    logger = tools.Logger()

    def fin():
        """Method executed after a joint test."""
        result_file_path = "/".join(
            [
                result_base_folder,
                joint_position_actuator.subdevice_type,
                joint_position_actuator.short_name
            ]) + ".csv"
        logger.log_file_write(result_file_path)

    request.addfinalizer(fin)
    # creating a dictionnary with all the objects
    dico_object = {
        "jointActuator": joint_position_actuator,
        "jointSensor": joint_position_sensor,
        "logger": logger
    }
    return dico_object


@pytest.fixture(scope="module")
def test_leg_dico(request, result_base_folder, dcm, mem):
    """
    Create the appropriate objects for each joint.
    It logs the informations into a dictionnary and save the data into a file
    after each joint test.
    """
    hippitch_position_actuator = subdevice.JointPositionActuator(
        dcm, mem, "HipPitch")
    hippitch_position_sensor = subdevice.JointPositionSensor(
        dcm, mem, "HipPitch")
    kneepitch_position_actuator = subdevice.JointPositionActuator(
        dcm, mem, "KneePitch")
    kneepitch_position_sensor = subdevice.JointPositionSensor(
        dcm, mem, "KneePitch")
    logger = tools.Logger()

    def fin():
        """Method executed after a joint test."""
        result_file_path = "/".join(
            [
                result_base_folder,
                hippitch_position_actuator.subdevice_type,
                "Leg"
            ]) + ".csv"
        logger.log_file_write(result_file_path)

    request.addfinalizer(fin)
    # creating a dictionnary with all the objects
    dico_object = {
        "hipActuator": hippitch_position_actuator,
        "hipSensor": hippitch_position_sensor,
        "kneeActuator": kneepitch_position_actuator,
        "kneeSensor": kneepitch_position_sensor,
        "logger": logger
    }
    return dico_object


@pytest.fixture(params=tools.use_section("joint_enslavement.cfg", "JulietteWheels"))
def test_wheels_dico(request, result_base_folder, dcm, mem):
    """
    Create the appropriate objects for each joint.
    It logs the informations into a dictionnary and save the data into a file
    after each wheel test.
    """
    wheel_speed_actuator = subdevice.WheelSpeedActuator(
        dcm, mem, request.param)
    wheel_speed_sensor = subdevice.WheelSpeedSensor(
        dcm, mem, request.param)
    logger = tools.Logger()

    def fin():
        """Method executed after a joint test."""
        result_file_path = "/".join(
            [
                result_base_folder,
                wheel_speed_actuator.subdevice_type,
                wheel_speed_actuator.short_name
            ]) + ".csv"
        logger.log_file_write(result_file_path)

    request.addfinalizer(fin)
    # creating a dictionnary with all the objects
    dico_object = {
        "wheelActuator": wheel_speed_actuator,
        "wheelSensor": wheel_speed_sensor,
        "logger": logger
    }
    return dico_object


@pytest.fixture(scope="module")
def test_time():
    """It returns the test time in milliseconds [ms]"""
    return int(tools.read_parameter(
        "joint_enslavement.cfg", "Parameters", "TestTime"))


@pytest.fixture(scope="module")
def test_limit():
    """It returns the limit error in degrees."""
    return float(tools.read_parameter(
        "joint_enslavement.cfg", "Parameters", "TestLimit"))


@pytest.fixture(scope="module")
def test_wheels_limit():
    """It returns the limit error in radians per seconds."""
    return float(tools.read_parameter(
        "joint_enslavement.cfg", "Parameters", "TestWheelsLimit"))
