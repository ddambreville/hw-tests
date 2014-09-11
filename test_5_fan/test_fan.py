import pytest
import tools
import subdevice
import fan_utils
from threading import Thread
import socket_connection


@pytest.mark.usefixtures("kill_motion", "stop_fans")
class TestFan:

    def test_fan_01(self, dcm, mem, plot, test_time, cycle_number,
                    result_base_folder, threshold):
        """
        FanBoard basic specification check.
        When fan actuator = 1 and fan speed is lower than the hald of its
        nominal speed, fan status must be set to 1.
        """
        # flags initialization
        fan_state = True

        # plot_server initialisation
        if plot:
            plot_server = socket_connection.Server()

        # objects initialization
        fan_hardness_actuator = subdevice.FanHardnessActuator(dcm, mem)
        right_fan_frequency = subdevice.FanFrequencySensor(dcm, mem, "Right")
        middle_fan_frequency = subdevice.FanFrequencySensor(dcm, mem, "Mid")
        left_fan_frequency = subdevice.FanFrequencySensor(dcm, mem, "Left")
        fan = subdevice.FanStatus(dcm, mem)

        # creating fan cycling behavior thread
        fan_behavior = Thread(
            target=fan_utils.fan_cycle, args=(dcm, mem, cycle_number))

        # starting behavior
        fan_behavior.start()

        # logger and timer objects creation
        logger = tools.Logger()
        timer = tools.Timer(dcm, 1000)

        # test loop
        while fan_behavior.isAlive():
            fan_hardness_value = fan_hardness_actuator.value
            right_fan_frequency_value = right_fan_frequency.value
            middle_fan_frequency_value = middle_fan_frequency.value
            left_fan_frequency_value = left_fan_frequency.value
            fan_status = fan.status
            dcm_time = timer.dcm_time() / 1000.

            # logging informations
            logger.log(
                ("Time", dcm_time),
                (fan_hardness_actuator.header_name, fan_hardness_value),
                (right_fan_frequency.header_name, right_fan_frequency_value),
                (middle_fan_frequency.header_name, middle_fan_frequency_value),
                (left_fan_frequency.header_name, left_fan_frequency_value),
                (fan.header_name, fan_status)
            )

            # for real time graphs
            if plot:
                plot_server.add_point(
                    fan_hardness_actuator.header_name, dcm_time,
                    fan_hardness_value)
                plot_server.add_point(
                    right_fan_frequency.header_name, dcm_time,
                    right_fan_frequency_value)
                plot_server.add_point(
                    middle_fan_frequency.header_name,
                    dcm_time, middle_fan_frequency_value)
                plot_server.add_point(
                    left_fan_frequency.header_name, dcm_time,
                    left_fan_frequency_value)
                plot_server.add_point(
                    fan.header_name, dcm_time, fan_status)

            # checking that fan status works well
            if fan_hardness_value == 1:
                if right_fan_frequency_value < threshold["RightFan"] and \
                    fan_status == 0:
                    fan_state = False
                if left_fan_frequency_value < threshold["LeftFan"] and \
                    fan_status == 0:
                    fan_state = False
                if middle_fan_frequency_value < threshold["MiddleFan"] and \
                    fan_status == 0:
                    fan_state = False

        file_name = "_".join(["Fan", str(fan_state)])
        result_file_path = "/".join([result_base_folder, file_name]) + ".csv"
        logger.log_file_write(result_file_path)

        assert fan_state
