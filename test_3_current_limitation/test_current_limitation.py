import pytest
import qha_tools
import subdevice
import math
import logging
import easy_plot_connection
import time

logging.basicConfig(level=logging.INFO)

@pytest.mark.usefixtures("kill_motion", "stiff_robot")
class TestCurrentLimitation:

    def test_joint_current_limitation(self, dcm, mem, parameters,
                                      joint, result_base_folder,
                                      rest_pos, stiffness_off,
                                      plot, plot_server):
        # logger initialization
        log = logging.getLogger('test_joint_current_limitation')

        # erasing real time plot
        plot_server.curves_erase()

        # flags initialization
        flag_loop = True  # test loop stops when this flag is False
        flag_joint = True  # giving test result
        flag_current_limit_low_exceeded = False

        # checking that ALMemory key MinMaxChange Allowed = 1
        if int(mem.getData("RobotConfig/Head/MinMaxChangeAllowed")) != 1:
            flag_loop = False
            log.error("MinMaxChangeAllowed ALMemory key missing")

        # test parameters
        test_params = parameters
        joint_position_actuator = joint.position.actuator
        joint_position_sensor = joint.position.sensor
        joint_temperature_sensor = joint.temperature
        joint_current_sensor = joint.current
        slav = qha_tools.SlidingAverage(test_params["sa_nb_points"])
        logger = qha_tools.Logger()

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

        # put joint to its initial maximum in 3 seconds
        if joint_position_actuator.short_name in\
         ("HipPitch", "RShoulderRoll", "RElbowRoll"):
            joint_position_actuator.qvalue = (joint_initial_minimum, 3000)
        else:
            joint_position_actuator.qvalue = (joint_initial_maximum, 3000)
        qha_tools.wait(dcm, 3000)

        # setting current limitations
        joint_max_current = joint_current_sensor.maximum
        joint_min_current = joint_current_sensor.minimum
        delta_current = joint_max_current - joint_min_current
        k_sup = test_params["limit_factor_sup"]
        k_inf = test_params["limit_factor_inf"]
        current_limit_high = joint_max_current + k_sup * delta_current
        current_limit_low = joint_max_current - k_inf * delta_current

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

        if joint_position_actuator.short_name in\
         ("HipPitch", "RShoulderRoll", "RElbowRoll"):
            joint_position_actuator.qvalue = (joint_new_minimum, 1000)
        else:
            joint_position_actuator.qvalue = (joint_new_maximum, 1000)

        timer = qha_tools.Timer(dcm, test_params["test_time"])
        timer_limit = qha_tools.Timer(dcm, test_params["test_time_limit"])

        # test loop
        while flag_loop and timer.is_time_not_out():
            try:
                loop_time = timer.dcm_time() / 1000.
                joint_temperature = joint_temperature_sensor.value
                joint_current = joint_current_sensor.value
                slav.point_add(joint_current)
                joint_current_sa = slav.calc()

                if not flag_current_limit_low_exceeded and\
                    joint_current_sa > current_limit_low:
                    flag_current_limit_low_exceeded = True
                    log.info("Current limit low exceeded")

                if joint_current_sa > current_limit_high:
                    flag_joint = False
                    log.warning("Current limit high overshoot")

                if flag_current_limit_low_exceeded and\
                    joint_current_sa < current_limit_low:
                    flag_joint = False
                    log.warning("Current lower than current limit low")

                if timer_limit.is_time_out() and not \
                    flag_current_limit_low_exceeded:
                    flag_joint = False
                    log.info("Timer limit finished and "+\
                        "current limit low not exceeded")

                # out of test loop if temperature is higher than min temperature
                if joint_temperature >= joint_temperature_min:
                    flag_loop = False
                    log.info("Temperature higher than Min temperature")
                    log.info("Test finished")

                logger.log(
                    ("Time", timer.dcm_time() / 1000.),
                    ("Current", joint_current),
                    ("CurrentSA", joint_current_sa),
                    ("CurrentLimitHigh", current_limit_high),
                    ("CurrentLimitLow", current_limit_low),
                    ("MaxAllowedCurrent", joint_max_current),
                    ("Temperature", joint_temperature),
                    ("TemperatureMin", joint_temperature_min),
                    ("Command", joint_position_actuator.value),
                    ("Position", joint_position_sensor.value)
                )

                if plot:
                    plot_server.add_point("Current", loop_time, joint_current)
                    plot_server.add_point("CurrentSA", loop_time,
                                          joint_current_sa)
                    plot_server.add_point("CurrentLimitHigh", loop_time,
                                          current_limit_high)
                    plot_server.add_point("CurrentLimitLow", loop_time,
                                          current_limit_low)
                    plot_server.add_point("MaxAllowedCurrent", loop_time,
                                          joint_max_current)
                    plot_server.add_point("Temperature", loop_time,
                                          joint_temperature)
                    plot_server.add_point("TemperatureMin", loop_time,
                                          joint_temperature_min)

            except KeyboardInterrupt:
                flag_loop = False  # out of test loop
                log.info("KeyboardInterrupt from user")

        log.info("OUT OF TEST LOOP")

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

        plot_server.curves_erase()

        assert flag_joint
        assert flag_current_limit_low_exceeded
