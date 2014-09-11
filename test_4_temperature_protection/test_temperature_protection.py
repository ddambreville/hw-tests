import pytest
import tools
import subdevice
import math
import socket_connection


@pytest.mark.usefixtures("kill_motion", "stiff_robot")
class TestCurrentLimitation:

    def test_joint_current_limitation(self, dcm, mem, parameters,
                                      test_objects_dico, result_base_folder,
                                      rest_pos, plot):
        # flags initialization
        flag_joint = True
        flag_loop = True
        flag_max_current_exceeded = False

        # plot_server initialisation
        if plot:
            plot_server = socket_connection.Server()

        # Objects creation
        test_params = parameters
        joint_position_actuator = test_objects_dico["jointPositionActuator"]
        joint_position_sensor = test_objects_dico["jointPositionSensor"]
        joint_temperature_sensor = test_objects_dico["jointTemperatureSensor"]
        joint_hardness_actuator = test_objects_dico["JointHardnessActuator"]
        joint_current_sensor = test_objects_dico["jointCurrentSensor"]
        slav = tools.SlidingAverage(test_params["sa_nb_points"])
        logger = tools.Logger()

        # Knowing the board, we can know if the motor is a MCC or DC Brushless
        joint_board = joint_position_actuator.device

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
        joint_current_max = joint_current_sensor.maximum
        joint_current_min = joint_current_sensor.minimum

        # setting temperature limitatons
        joint_temperature_min = joint_temperature_sensor.minimum
        joint_temperature_max = joint_temperature_sensor.maximum
        delta_temperature = joint_temperature_max - joint_temperature_min

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

        # set timers
        if joint_position_actuator.short_name in ("KneePitch", "HipPitch"):
            timer = tools.Timer(dcm, 60000)
            timer_limit = tools.Timer(dcm, 3000)
        else:
            timer = tools.Timer(dcm, test_params["test_time"])
            timer_limit = tools.Timer(dcm, test_params["test_time_limit"])

        # set position actuator out of the joint mechanical stop
        if joint_position_actuator.short_name in ("HipPitch", "RShoulderRoll"):
            joint_position_actuator.qvalue = (joint_new_minimum, 1000)
        else:
            joint_position_actuator.qvalue = (joint_new_maximum, 1000)

        while flag_loop is True and timer.is_time_not_out():

            joint_temperature = joint_temperature_sensor.value
            joint_current = joint_current_sensor.value
            slav.point_add(joint_current)
            joint_position_command = joint_position_actuator.value
            joint_position = joint_position_sensor.value
            joint_hardness_value = joint_hardness_actuator.value
            joint_current_sa = slav.calc()
            dcm_time = timer.dcm_time() / 1000.

            # Max current adaptation if joint temperature higher than Min
            # No lower current for DC Brushless motors
            if joint_board not in \
                ("HipBoard", "ThighBoard", "BackPlatformBoard"):
                if joint_temperature > joint_temperature_min:
                    overheat = joint_temperature - joint_temperature_min

                    if overheat > delta_temperature:
                        overheat = delta_temperature
                    if overheat < 1:
                        overheat = 1

                    max_allowed_current = \
                        parameters["temperature_coeffs"][
                            int(overheat) - 1] * joint_current_max / 1000.
                else:
                    max_allowed_current = joint_current_max
            else:
                max_allowed_current = joint_current_max

            # defining current regulation limits
            current_limit_high = max_allowed_current + \
                parameters["limit_factor"] * \
                (max_allowed_current - joint_current_min)
            current_limit_low = max_allowed_current - \
                parameters["limit_factor"] * \
                (max_allowed_current - joint_current_min)

            # setting flag if max current exceeded
            if joint_current_sa > max_allowed_current:
                flag_max_current_exceeded = True

            # averaged current has not to exceed limit high
            if joint_current_sa > current_limit_high:
                flag_joint = False
                flag_loop = False

            # once max current is exceeded, current hasn't to be lower than
            # limit low
            if flag_max_current_exceeded and \
                joint_current_sa < current_limit_low:
                flag_joint = False

            # after time limit, current has to have exceeded max current
            if timer_limit.is_time_out() and not flag_max_current_exceeded:
                flag_joint = False

            if joint_temperature > joint_temperature_max + 3:
                flag_loop = False
                flag_joint = False

            logger.log(
                ("Time", dcm_time),
                ("Hardness", joint_hardness_value),
                ("Current", joint_current),
                ("CurrentSA", joint_current_sa),
                ("MaxAllowedCurrent", max_allowed_current),
                ("CurrentLimitHigh", current_limit_high),
                ("CurrentLimitLow", current_limit_low),
                ("Temperature", joint_temperature),
                ("TemperatureMin", joint_temperature_min),
                ("TemperatureMax", joint_temperature_max),
                ("Command", joint_position_command),
                ("Position", joint_position)
            )

            # for real time plot
            if plot:
                plot_server.add_point(
                    "Hardness", dcm_time, joint_hardness_value)
                plot_server.add_point("Current", dcm_time, joint_current)
                plot_server.add_point("CurrentSA", dcm_time, joint_current_sa)
                plot_server.add_point(
                    "MaxAllowedCurrent", dcm_time, max_allowed_current)
                plot_server.add_point(
                    "CurrentLimitHigh", dcm_time, current_limit_high)
                plot_server.add_point(
                    "CurrentLimitLow", dcm_time, current_limit_low)
                plot_server.add_point(
                    "Temperature", dcm_time, joint_temperature)
                plot_server.add_point(
                    "TemperatureMin", dcm_time, joint_temperature_min)
                plot_server.add_point(
                    "TemperatureMax", dcm_time, joint_temperature_max)
                plot_server.add_point(
                    "Command", dcm_time, joint_position_command)
                plot_server.add_point(
                    "Position", dcm_time, joint_position)

        # writing logger results into a csv file
        result_file_path = "/".join(
            [
                result_base_folder,
                joint_position_actuator.subdevice_type,
                joint_position_actuator.short_name + "_" + str(flag_joint)
            ]) + ".csv"
        logger.log_file_write(result_file_path)

        # seting min and max joint software limits to their original values
        joint_position_actuator.maximum = [
            [[joint_initial_maximum, dcm.getTime(0)]], "Merge"]
        joint_position_actuator.minimum = [
            [[joint_initial_minimum, dcm.getTime(0)]], "Merge"]

        assert flag_joint
        assert flag_max_current_exceeded
