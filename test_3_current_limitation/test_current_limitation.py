import pytest
import tools
import subdevice
import math


@pytest.mark.usefixtures("kill_motion", "stiff_robot")
class TestCurrentLimitation:

    def test_joint_current_limitation(self, dcm, mem, parameters,
                                      test_objects_dico, result_base_folder,
                                      rest_pos):
        # flags initialization
        flag_joint = True
        flag_max_current_exceeded = False

        # test parameters
        test_params = parameters
        joint_position_actuator = test_objects_dico["jointPositionActuator"]
        joint_position_sensor = test_objects_dico["jointPositionSensor"]
        joint_temperature_sensor = test_objects_dico["jointTemperatureSensor"]
        joint_current_sensor = test_objects_dico["jointCurrentSensor"]
        slav = tools.SlidingAverage(test_params["sa_nb_points"])
        logger = tools.Logger()

        # Going to initial position
        subdevice.multiple_set(dcm, mem, rest_pos, wait=True)

        # keeping initial joint min and max
        joint_initial_maximum = joint_position_actuator.maximum
        joint_initial_minimum = joint_position_actuator.minimum

        # put joint to its initial maximum in 3 seconds
        if joint_position_actuator.short_name in ("HipPitch", "RShoulderRoll"):
            joint_position_actuator.qvalue = (joint_initial_minimum, 3000)
        else:
            joint_position_actuator.qvalue = (joint_initial_maximum, 3000)
        tools.wait(dcm, 3000)

        # setting current limitations
        joint_max_current = joint_current_sensor.maximum
        joint_min_current = joint_current_sensor.minimum
        delta_current = joint_max_current - joint_min_current
        k = test_params["limit_factor"]
        current_limit_high = joint_max_current + k * delta_current
        current_limit_low = joint_max_current - k * delta_current

        # setting temperature limitatons
        joint_temperature_min = joint_temperature_sensor.minimum

        # setting new min and max out of the mechanical stop
        joint_new_maximum = \
            joint_initial_maximum + \
            math.radians(test_params["limit_extension"])

        joint_new_minimum = \
            joint_initial_minimum - \
            math.radians(test_params["limit_extension"])

        joint_position_actuator.maximum = [
            [[joint_new_maximum, dcm.getTime(0)]], "Merge"]
        joint_position_actuator.minimum = [
            [[joint_new_minimum, dcm.getTime(0)]], "Merge"]

        if joint_position_actuator.short_name in ("HipPitch", "RShoulderRoll"):
            joint_position_actuator.qvalue = (joint_new_minimum, 1000)
        else:
            joint_position_actuator.qvalue = (joint_new_maximum, 1000)

        if joint_position_actuator.short_name in ("KneePitch", "HipPitch"):
            timer = tools.Timer(dcm, 6000)
            timer_limit = tools.Timer(dcm, 3000)
        else:
            timer = tools.Timer(dcm, test_params["test_time"])
            timer_limit = tools.Timer(dcm, test_params["test_time_limit"])

        while flag_joint is True and timer.is_time_not_out():

            joint_temperature = joint_temperature_sensor.value
            joint_current = joint_current_sensor.value
            slav.point_add(joint_current)
            joint_current_sa = slav.calc()

            if joint_current_sa > joint_max_current:
                flag_max_current_exceeded = True

            if joint_current_sa > current_limit_high:
                flag_joint = False

            if flag_max_current_exceeded and\
                joint_current_sa < current_limit_low:
                flag_joint = False

            if timer_limit.is_time_out() and not flag_max_current_exceeded:
                flag_joint = False

            if joint_temperature >= joint_temperature_min:
                flag_joint = None

            logger.log(
                ("Time", timer.dcm_time() / 1000.),
                ("Current", joint_current),
                ("CurrentSA", joint_current_sa),
                ("CurrentLimitHigh", current_limit_high),
                ("CurrentLimitLow", current_limit_low),
                ("MaxCurrent", joint_max_current),
                ("Temperature", joint_temperature),
                ("TemperatureMax", joint_temperature_min),
                ("Command", joint_position_actuator.value),
                ("Position", joint_position_sensor.value)
            )

        result_file_path = "/".join(
            [
                result_base_folder,
                joint_position_actuator.subdevice_type,
                joint_position_actuator.short_name + "_" + str(flag_joint)
            ]) + ".csv"
        logger.log_file_write(result_file_path)

        joint_position_actuator.maximum = [
            [[joint_initial_maximum, dcm.getTime(0)]], "Merge"]
        joint_position_actuator.minimum = [
            [[joint_initial_minimum, dcm.getTime(0)]], "Merge"]

        assert flag_joint
        assert flag_max_current_exceeded
