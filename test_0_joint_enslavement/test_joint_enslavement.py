import tools
import subdevice
import math

def test_joint_enslavement(dcm, mem, kill_motion, zero_pos, test_objects_dico, test_time, test_limit):
    """Test joint enslavement. Error must be lower than a fixed limit."""
    # Objects creation
    joint_position_actuator = test_objects_dico["jointActuator"]
    joint_position_sensor = test_objects_dico["jointSensor"]
    logger = test_objects_dico["logger"]

    # Flag initialization
    flag = True

    # Going to initial position
    subdevice.multiple_set(dcm, mem, zero_pos, wait=True)

    # Behavior of the tested part
    joint_position_actuator.explore(2*test_time)

    # Timer creation just before test loop
    timer = tools.Timer(dcm, 4*test_time)

    # Test loop
    while timer.is_time_not_out():
        error = joint_position_actuator.value - joint_position_sensor.value
        logger.log(
            ("Time", timer.dcm_time() / 1000.),
            ("Actuator", math.degrees(joint_position_actuator.value)),
            ("Position", math.degrees(joint_position_sensor.value)),
            ("Error", math.degrees(error)),
            ("Max", test_limit),
            ("-Max", test_limit*-1.))

        if abs(error) > math.radians(test_limit):
            flag = False

    assert flag

def test_leg_enslavement(dcm, mem, kill_motion, zero_pos, test_leg_dico, test_time, test_limit):
    """
    Test joint enslavement for HipPitch and KneePitch.
    Error must be lower than a fixed limit.
    """
    # Objects creation
    hippitch_position_actuator = test_leg_dico["hipActuator"]
    hippitch_position_sensor = test_leg_dico["hipSensor"]
    kneepitch_position_actuator = test_leg_dico["kneeActuator"]
    kneepitch_position_sensor = test_leg_dico["kneeSensor"]
    logger = test_leg_dico["logger"]

    # Flag initialization
    flag = True

    # Going to initial position
    subdevice.multiple_set(dcm, mem, zero_pos, wait=True)

    # Behavior of the tested part
    hippitch_position_actuator.explore(2*test_time)
    kneepitch_position_actuator.explore(2*test_time, max_to_min=False)

    # Timer creation just before test loop
    timer = tools.Timer(dcm, 4*test_time)

    # Test loop
    while timer.is_time_not_out():
        error_hip = hippitch_position_actuator.value - hippitch_position_sensor.value
        error_knee = kneepitch_position_actuator.value - kneepitch_position_sensor.value

        logger.log(
            ("Time", timer.dcm_time() / 1000.),
            ("HipPitchActuator",
             math.degrees(hippitch_position_actuator.value)),
            ("HipPitchPosition", math.degrees(hippitch_position_sensor.value)),
            ("ErrorHip", math.degrees(error_hip)),
            ("KneePitchActuator",
             math.degrees(kneepitch_position_actuator.value)),
            ("KneePitchPosition",
             math.degrees(kneepitch_position_sensor.value)),
            ("ErrorKnee", math.degrees(error_knee)),
            ("Max", test_limit),
            ("-Max", test_limit*-1.))

        if(abs(error_hip)>math.radians(test_limit) or abs(error_knee)>math.radians(test_limit)):
            flag = False

    assert flag

def test_wheels_enslavement(dcm, mem, kill_motion, zero_pos, test_wheels_dico, stiff_robot_wheels, test_time, test_wheels_limit):
    """
    Test wheels enslavement.
    Error must be lower than a fixed limit (here test_wheels_limit).
    """
    # Objects creation
    wheel_speed_actuator = test_wheels_dico["wheelActuator"]
    wheel_speed_sensor = test_wheels_dico["wheelSensor"]
    logger = test_wheels_dico["logger"]
    sliding_avg = tools.SlidingAverage(3)

    # Flag initialization
    flag = True

    # Going to initial position
    #subdevice.multiple_set(dcm, mem, zero_pos, wait=True)

    # Behavior of the tested part
    wheel_speed_actuator.trapeze(
        0.1, 1000., 2000., sens="positive", second_invert_trapeze=True)

    # Timer creation just before test loop
    timer = tools.Timer(dcm, 4*test_time)

    # Test loop
    while timer.is_time_not_out():
        speed_actuator = wheel_speed_actuator.value
        speed_sensor = wheel_speed_sensor.value

        # Calculating an averaged sensor value on 3 points. The error can
        # dynamically be high because of the wheel mechanic.
        sliding_avg.point_add(speed_sensor)
        speed_sensor_sa = sliding_avg.calc()

        error = speed_actuator - speed_sensor
        error_sa = speed_actuator - speed_sensor_sa

        # Logging usefull information
        logger.log(
            ("Time", timer.dcm_time() / 1000.),
            ("Actuator", wheel_speed_actuator.value),
            ("Speed", speed_sensor),
            ("SpeedSA", speed_sensor_sa),
            ("Error", error),
            ("ErrorSA", error_sa),
            ("Max", test_wheels_limit),
            ("-Max", test_wheels_limit*-1.))

        # Checking that enslavement is good
        if abs(error_sa) > test_wheels_limit:
            flag = False

    assert flag
