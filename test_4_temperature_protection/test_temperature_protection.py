import pytest
import qha_tools
import subdevice
import device
import math
import easy_plot_connection
import logging
import time
import datetime

# Creating log file
DATE = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
logging.basicConfig(
    filename='Results/'+str(DATE)+'.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

@pytest.mark.usefixtures("kill_motion", "stiff_robot")
class TestTemperatureProtection:

    def test_joint_temperature_protection(self, dcm, mem, parameters,
                                          joint, result_base_folder,
                                          rest_pos, stiffness_off,
                                          plot_server, plot):
        # logger initialization
        log = logging.getLogger('MOTOR_LIMITATION_PERF_HW_002')

        # flags initialization
        flag_joint = True
        flag_loop = True
        flag_max_current_exceeded = False
        flag_max_temperature_exceeded = False
        flag_low_limit = False
        flag_info = False
        flag_info2 = False
        flag_info3 = False
        flag_info4 = False

        # erasing real time curves
        if plot:
            plot_server.curves_erase()

        # Objects creation
        test_params = parameters
        joint_position_actuator = joint.position.actuator
        joint_position_sensor = joint.position.sensor
        joint_temperature_sensor = joint.temperature
        joint_hardness_actuator = joint.hardness
        joint_current_sensor = joint.current
        slav = qha_tools.SlidingAverage(test_params["sa_nb_points"])
        logger = qha_tools.Logger()

        log.info("")
        log.info("*************************************")
        log.info("Testing : " + str(joint.short_name))
        log.info("*************************************")
        log.info("")

        # Knowing the board, we can know if the motor is a MCC or DC Brushless
        joint_board = joint_position_actuator.device

        # Creating device object to acceed to its error
        joint_board_object = device.Device(dcm, mem, joint_board)

        # Going to initial position
        subdevice.multiple_set(dcm, mem, rest_pos, wait=True)
        # unstiffing all the other joints to avoid leg motors overheat
        subdevice.multiple_set(dcm, mem, stiffness_off, wait=False)
        time.sleep(0.1)

        # stiffing the joint we want to test
        joint.hardness.qqvalue = 1.0

        # keeping initial joint min and max
        joint_initial_maximum = joint_position_actuator.maximum
        joint_initial_minimum = joint_position_actuator.minimum

        # setting current limitations
        joint_current_max = joint_current_sensor.maximum

        # setting temperature limitatons
        joint_temperature_min = joint_temperature_sensor.minimum
        joint_temperature_max = joint_temperature_sensor.maximum
        delta_temperature = joint_temperature_max - joint_temperature_min

        # setting new min and max out of the mechanical stop
        if joint_initial_maximum >= 0.0:
            joint_new_maximum = \
                joint_initial_maximum + \
                math.radians(test_params["limit_extension"])
        else:
            joint_new_maximum = \
                joint_initial_maximum - \
                math.radians(test_params["limit_extension"])

        if joint_initial_minimum <= 0.0:
            joint_new_minimum = \
                joint_initial_minimum - \
                math.radians(test_params["limit_extension"])
        else:
            joint_new_minimum = \
                joint_initial_minimum + \
                math.radians(test_params["limit_extension"])

        joint_position_actuator.maximum = [
            [[joint_new_maximum, dcm.getTime(0)]], "Merge"]
        joint_position_actuator.minimum = [
            [[joint_new_minimum, dcm.getTime(0)]], "Merge"]

        # set timer limit
        timer_limit = qha_tools.Timer(dcm, test_params["test_time_limit"])

        # for Brushless motors, max test time is 60 seconds
        brushless_motors = ("KneePitch", "HipPitch", "HipRoll")
        if joint_position_actuator.short_name in brushless_motors:
            timer = qha_tools.Timer(dcm, 60000)
        else:
            timer = qha_tools.Timer(dcm, test_params["test_time"])

        # set position actuator out of the joint mechanical stop
        # going out of physical mechanical stop in 5 seconds
        if joint_position_actuator.short_name in \
            ("HipPitch", "RShoulderRoll", "HipRoll"):
            joint_position_actuator.qvalue = (joint_new_minimum, 5000)
        else:
            joint_position_actuator.qvalue = (joint_new_maximum, 5000)

        flag_first_iteration = True
        timer_current_decrease = qha_tools.Timer(dcm, 100)
        while flag_loop is True and timer.is_time_not_out():
            try:
                joint_temperature = joint_temperature_sensor.value
                joint_current = joint_current_sensor.value
                slav.point_add(joint_current)
                joint_position_command = joint_position_actuator.value
                joint_position = joint_position_sensor.value
                joint_hardness_value = joint_hardness_actuator.value
                joint_current_sa = slav.calc()
                firmware_error = joint_board_object.error
                dcm_time = timer.dcm_time() / 1000.

                # Max current adaptation if joint temperature higher than Min
                # No lower current for DC Brushless motors
                if joint_board not in \
                    ("HipBoard", "ThighBoard", "BackPlatformBoard"):
                    if joint_temperature > joint_temperature_min:
                        delta_max = joint_temperature_max - joint_temperature
                        max_allowed_current = (
                            (delta_max) / (delta_temperature)) *\
                        joint_current_max
                    else:
                        max_allowed_current = joint_current_max
                else:
                    max_allowed_current = joint_current_max

                # max allowed current can not be lower than 0.
                if max_allowed_current < 0.0:
                    max_allowed_current = 0.0

                # defining old max current as first calculated max current if
                # it is the first loop iteration
                if flag_first_iteration is True:
                    old_mac = max_allowed_current
                    flag_first_iteration = False

                # defining current regulation limits
                current_limit_high = max_allowed_current * \
                (1.0 + test_params["limit_factor_sup"])
                current_limit_low = max_allowed_current *\
                (1.0 - test_params["limit_factor_inf"])

                # setting flag to True if 90 percent of max current is exceeded
                if joint_current_sa > 0.9 * max_allowed_current and not\
                 flag_max_current_exceeded:
                    flag_max_current_exceeded = True
                    log.info("90 percent of max allowed currend reached")

                if max_allowed_current != old_mac:
                    timer_current_decrease = qha_tools.Timer(dcm, 100)

                # averaged current has not to exceed limit high
                if joint_current_sa > current_limit_high and \
                    timer_current_decrease.is_time_out() and not flag_info4:
                    flag_joint = False
                    flag_info4 = True
                    log.warning("current high limit exceeded")

                # once max current is exceeded, current hasn't to be lower than
                # limit low
                if flag_max_current_exceeded and \
                    joint_current_sa < current_limit_low and not \
                    flag_max_temperature_exceeded and not flag_low_limit:
                    flag_joint = False
                    flag_low_limit = True
                    log.info("current has been lower than low limit")

                # after time limit, current has to have exceeded max current
                # if it has not, it is written on time in log file
                if timer_limit.is_time_out() and not\
                 flag_max_current_exceeded and flag_info is False:
                    flag_joint = False
                    flag_info = True
                    log.info("current has not exceeded 90 percent of max "+\
                        "allowed current")

                # hardware protection
                if joint_temperature >= joint_temperature_max + 1:
                    flag_loop = False
                    log.warning("temperature too high (max+1 degree)")

                # if joint temperature higher than a limit value,
                # joint current must be null after 100ms.
                if flag_max_temperature_exceeded is False and \
                    joint_temperature >= joint_temperature_max:
                    flag_max_temperature_exceeded = True
                    timer_max = qha_tools.Timer(dcm, 100)
                    log.info("max temperature exceeded a first time")

                if flag_max_temperature_exceeded and\
                timer_max.is_time_out() and joint_current != 0 and not\
                flag_info2:
                    flag_joint = False
                    flag_info2 = True
                    log.critical("max temperature exceeded and current "+\
                        "is not null")

                if flag_max_temperature_exceeded and joint_current == 0.0 and\
                not flag_info3:
                    flag_info3 = True
                    log.info("current null reached")

                old_mac = max_allowed_current

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
                    ("Position", joint_position),
                    ("FWError", firmware_error)
                )

                # for real time plot
                if plot:
                    plot_server.add_point(
                        "Hardness", dcm_time, joint_hardness_value)
                    plot_server.add_point(
                        "CurrentSA", dcm_time, joint_current_sa)
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

            except KeyboardInterrupt:
                flag_loop = False
                log.info("KeyboardInterrupt from user")

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
