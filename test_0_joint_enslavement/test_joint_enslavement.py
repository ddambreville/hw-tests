import qha_tools
import subdevice
import math
import pytest


@pytest.mark.usefixtures("kill_motion", "stiff_robot")
class TestEnslavement:

    """
    Test class which contains enslavement tests for:
    - Joints
    - Leg (HipPitch + KneePitch)
    - Wheels
    """

    def test_joint_enslavement(self, dcm, mem, zero_pos, test_objects_dico,
                               test_time):
        """
        Test joint enslavement.
        Error must be lower than a fixed limit.

        @type  dcm        : object
        @param dcm        : proxy to DCM
        @type mem         : object
        @param mem        : proxy to ALMemory
        @type zero_pos    : dictionnary
        @param zero_pos   : dictionnary {"ALMemory key":value} from config file.
        @type joint       : string
        @param joint      : string describing the current joint.
        @type test_time   : integer
        @param test_time  : time to wait to test a joint enslavement [ms].
        """
        # Objects creation
        joint_position_actuator = test_objects_dico["jointActuator"]
        joint_position_sensor = test_objects_dico["jointSensor"]
        logger = test_objects_dico["logger"]
        test_limit = test_objects_dico["joint_test_limit"]

        # Flag initialization
        logger.flag = True

        # Going to initial position
        subdevice.multiple_set(dcm, mem, zero_pos, wait=True)

        # Going to min position to have a complete exploration
        joint_position_actuator.go_to(dcm, "min")

        # Behavior of the tested part
        joint_position_actuator.explore(2 * test_time)

        # Timer creation just before test loop
        timer = qha_tools.Timer(dcm, 4 * test_time)

        # Test loop
        while timer.is_time_not_out():
            error = joint_position_actuator.value - joint_position_sensor.value
            actuator_degrees = math.degrees(joint_position_actuator.value)
            logger.log(
                ("Time", timer.dcm_time() / 1000.),
                ("Actuator", actuator_degrees),
                ("Sensor", math.degrees(joint_position_sensor.value)),
                ("Error", math.degrees(error)),
                ("Eps", test_limit),
                ("-Eps", test_limit * -1.),
                ("Actuator+Eps", actuator_degrees + test_limit),
                ("Actuator-Eps", actuator_degrees - test_limit)
            )

            if abs(error) > math.radians(test_limit):
                logger.flag = False

        assert logger.flag

    def test_leg_enslavement(self, dcm, mem, zero_pos, test_leg_dico,
                             test_time, test_limit):
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
        logger.flag = True

        # Going to initial position
        subdevice.multiple_set(dcm, mem, zero_pos, wait=True)

        # Behavior of the tested part
        hippitch_position_actuator.explore(2 * test_time)
        kneepitch_position_actuator.explore(2 * test_time, max_to_min=False)

        # Timer creation just before test loop
        timer = qha_tools.Timer(dcm, 4 * test_time)

        # Test loop
        while timer.is_time_not_out():
            hip_act_rad = hippitch_position_actuator.value
            hip_act_deg = math.degrees(hip_act_rad)
            hip_sensor_rad = hippitch_position_sensor.value
            hip_sensor_deg = math.degrees(hip_sensor_rad)

            knee_act_rad = kneepitch_position_actuator.value
            knee_act_deg = math.degrees(knee_act_rad)
            knee_sensor_rad = kneepitch_position_sensor.value
            knee_sensor_deg = math.degrees(knee_sensor_rad)

            error_hip = hip_act_deg - hip_sensor_deg
            error_knee = knee_act_deg - knee_sensor_deg

            logger.log(
                ("Time", timer.dcm_time() / 1000.),
                ("HipPitchActuator", hip_act_deg),
                ("HipPitchSensor", hip_sensor_deg),
                ("ErrorHip", error_hip),
                ("KneePitchActuator", knee_act_deg),
                ("KneePitchSensor", knee_sensor_deg),
                ("ErrorKnee", error_knee),
                ("Eps", test_limit),
                ("-Eps", test_limit * -1.),
                ("HipPitchActuator+Eps", hip_act_deg + test_limit),
                ("HipPitchActuator-Eps", hip_act_deg - test_limit),
                ("KneePitchActuator+Eps", knee_act_deg + test_limit),
                ("KneePitchActuator-Eps", knee_act_deg - test_limit)
            )

            if abs(error_hip) > test_limit or abs(error_knee) > test_limit:
                logger.flag = False

        assert logger.flag

    def test_wheels_enslavement(self, dcm, mem, zero_pos, test_wheels_dico,
                                stiff_robot_wheels, test_time,
                                test_wheels_limit):
        """
        Test wheels enslavement.
        Error must be lower than a fixed limit (here test_wheels_limit).
        """
        # Objects creation
        wheel_speed_actuator = test_wheels_dico["wheelActuator"]
        wheel_speed_sensor = test_wheels_dico["wheelSensor"]
        logger = test_wheels_dico["logger"]
        sliding_avg = qha_tools.SlidingAverage(3)

        # Flag initialization
        logger.flag = True

        # Going to initial position
        #subdevice.multiple_set(dcm, mem, zero_pos, wait=True)

        # Behavior of the tested part
        wheel_speed_actuator.trapeze(
            0.1, 1000., 2000., sens="positive", second_invert_trapeze=True)

        # Timer creation just before test loop
        timer = qha_tools.Timer(dcm, 4 * test_time)

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
            actuator = wheel_speed_actuator.value

            # Logging usefull information
            logger.log(
                ("Time", timer.dcm_time() / 1000.),
                ("Actuator", actuator),
                ("Sensor", speed_sensor),
                ("SpeedSA", speed_sensor_sa),
                ("Error", error),
                ("ErrorSA", error_sa),
                ("Eps", test_wheels_limit),
                ("-Eps", test_wheels_limit * -1.),
                ("Actuator+Eps", actuator + test_wheels_limit),
                ("Actuator-Eps", actuator - test_wheels_limit)
            )

            # Checking that enslavement is good
            if abs(error_sa) > test_wheels_limit:
                logger.flag = False

        assert logger.flag
