import pytest
import threading
import easy_plot_connection
import time


class Plot(threading.Thread):

    """
    Class to log during test
    """

    def __init__(self, joint, mem, event, joint_pos_act, joint_pos_sen,
                 joint_speed_act, joint_speed_sen, limit_position,
                 limit_speed):
        threading.Thread.__init__(self)
        self._name = joint
        self._mem = mem
        self._event = event
        self._joint_position_actuator = joint_pos_act
        self._joint_position_sensor = joint_pos_sen
        self._joint_speed_actuator = joint_speed_act
        self._joint_speed_sensor = joint_speed_sen
        self._limit_position = limit_position
        self._limit_speed = limit_speed

        self._end = False

    def run(self):
        """ Log """

        plot_server = easy_plot_connection.Server(local_plot=True)
        plot_server.curves_erase()

        log_file = open(self._name + ".csv", 'w')
        line_to_write = ";".join([
            "Time",
            "Event",
            "EventType",
            "PositionActuator",
            "PositionSensor",
            "ErrorPosition",
            "SpeedActuator",
            "SpeedSensor",
            "ErrorSpeed"
        ]) + "\n"
        log_file.write(line_to_write)
        log_file.flush()

        time_init = time.time()
        while not self._end:
            elapsed_time = time.time() - time_init
            plot_server.add_point(
                "PositionError",
                elapsed_time,
                self._joint_position_actuator.value -
                self._joint_position_sensor.value
            )
            plot_server.add_point(
                "SpeedError",
                elapsed_time,
                self._joint_speed_actuator.value -
                self._joint_speed_sensor.value
            )
            plot_server.add_point(
                "MaxLimitErrorPosition",
                elapsed_time,
                self._limit_position
            )
            plot_server.add_point(
                "MinLimitErrorPosition",
                elapsed_time,
                -self._limit_position
            )
            plot_server.add_point(
                "MaxLimitErrorSpeed",
                elapsed_time,
                self._limit_speed
            )
            plot_server.add_point(
                "MinLimitErrorSpeed",
                elapsed_time,
                -self._limit_speed
            )
            plot_server.add_point(
                "Event",
                elapsed_time,
                self._event.flag_event
            )

            event = self._mem.getData("TouchChanged")

            line_to_write = ";".join([
                str(elapsed_time),
                str(self._event.flag_event),
                str(event),
                str(self._joint_position_actuator.value),
                str(self._joint_position_sensor.value),
                str(self._joint_position_actuator.value -
                    self._joint_position_sensor.value),
                str(self._joint_speed_actuator.value),
                str(self._joint_speed_sensor.value),
                str(self._joint_speed_actuator.value -
                    self._joint_speed_sensor.value),
            ]) + "\n"
            log_file.write(line_to_write)
            log_file.flush()

            time.sleep(0.1)

        plot_server.stop()

    def stop(self):
        """ To stop logging """
        self._end = True
