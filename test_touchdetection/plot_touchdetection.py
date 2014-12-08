import pytest
import threading
import easy_plot_connection
import time


class Plot(threading.Thread):

    """
    Class to log during test
    """

    def __init__(self, joint, mem, event, joint_pos_act, joint_pos_sen,
                 joint_speed_act, joint_speed_sen, joint_temp, limit_position,
                 limit_speed, temp_max, temp_max_to_start):
        """
        @joint                  : joint name (string)
        @mem                    : proxy to Motion (object)
        @event                  : event flag (integer)
        @joint_pos_act          : joint position actuator object (object)
        @joint_pos_sen          : joint position sensor object (object)
        @joint_speed_act        : joint speed actuator object (object)
        @joint_speed_sen        : joint speed sensor object (object)
        @joint_temp             : joint temperature object (object)
        @limit_position         : limit position (integer)
        @limit_speed            : limit speed (integer)
        @temp_max               : maximal joint temperature permitted (integer)
        @temp_max_to_start      : maximal joint temperature permitted to start
                                  (integer)
        """

        threading.Thread.__init__(self)
        self._name = joint
        self._mem = mem
        self._event = event
        self._joint_position_actuator = joint_pos_act
        self._joint_position_sensor = joint_pos_sen
        self._joint_speed_actuator = joint_speed_act
        self._joint_speed_sensor = joint_speed_sen
        self._joint_temperature = joint_temp
        self._limit_position = limit_position
        self._limit_speed = limit_speed
        self._temp_max = temp_max
        self._temp_max_to_start = temp_max_to_start

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
            "MaxLimitErrorPosition",
            "MinLimitErrorPosition",
            "SpeedActuator",
            "SpeedSensor",
            "ErrorSpeed",
            "MaxLimitErrorSpeed",
            "MinLimitErrorSpeed",
            "Temperature",
            "TemperatureMin",
            "TemperatureMax"
        ]) + "\n"
        log_file.write(line_to_write)
        log_file.flush()

        time_init = time.time()
        while not self._end:
            elapsed_time = time.time() - time_init
            plot_server.add_point(
                "PositionActuator",
                elapsed_time,
                self._joint_position_actuator.value
            )
            plot_server.add_point(
                "PositionSensor",
                elapsed_time,
                self._joint_position_sensor.value
            )
            plot_server.add_point(
                "PositionError",
                elapsed_time,
                self._joint_position_actuator.value -
                self._joint_position_sensor.value
            )
            plot_server.add_point(
                "SpeedActuator",
                elapsed_time,
                self._joint_speed_actuator.value
            )
            plot_server.add_point(
                "SpeedSensor",
                elapsed_time,
                self._joint_speed_sensor.value
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
            plot_server.add_point(
                "Temperature",
                elapsed_time,
                self._joint_temperature.value
            )
            plot_server.add_point(
                "TemperatureMin",
                elapsed_time,
                self._temp_max_to_start
            )
            plot_server.add_point(
                "TemperatureMax",
                elapsed_time,
                self._temp_max
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
                str(self._limit_position),
                str(-self._limit_position),
                str(self._joint_speed_actuator.value),
                str(self._joint_speed_sensor.value),
                str(self._joint_speed_actuator.value -
                    self._joint_speed_sensor.value),
                str(self._limit_speed),
                str(-self._limit_speed),
                str(self._joint_temperature.value),
                str(self._temp_max_to_start),
                str(self._temp_max)
            ]) + "\n"
            log_file.write(line_to_write)
            log_file.flush()

            time.sleep(0.1)

        plot_server.stop()

    def stop(self):
        """ To stop logging """
        self._end = True
