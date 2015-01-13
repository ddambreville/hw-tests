import pytest
import threading
import time


class Log(threading.Thread):

    """
    Class to log during test
    """

    def __init__(self, joint, speed, mem, event, joint_pos_act, joint_pos_sen,
                 joint_speed_act, joint_speed_sen, joint_temp, joint_hardness,
                 limit_position, limit_speed, temp_max, temp_max_to_start):
        """
        @joint                  : joint name (string)
        @Speed                  : speed (float)
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
        self._speed = str(speed)
        self._mem = mem
        self._event = event
        self._joint_position_actuator = joint_pos_act
        self._joint_position_sensor = joint_pos_sen
        self._joint_speed_actuator = joint_speed_act
        self._joint_speed_sensor = joint_speed_sen
        self._joint_temperature = joint_temp
        self._joint_hardness = joint_hardness
        self._limit_position = limit_position
        self._limit_speed = limit_speed
        self._temp_max = temp_max
        self._temp_max_to_start = temp_max_to_start

        self._end = False

    def run(self):
        """ Log """

        log_file = open(self._name + "-" + self._speed + ".csv", 'w')
        line_to_write = ",".join([
            "Time",
            "Event",
            "EventType",
            "Hardness",
            "PositionActuator",
            "PositionSensor",
            "PositionError",
            "MaxLimitErrorPosition",
            "MinLimitErrorPosition",
            "SpeedActuator",
            "SpeedSensor",
            "SpeedError",
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

            event = str(self._mem.getData("TouchChanged"))
            # Remove , to avoid conflict in csv file
            event = event.replace(',', '')

            line_to_write = ",".join([
                str(elapsed_time),
                str(self._event.flag_event),
                event,
                str(self._joint_hardness.value),
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

    def stop(self):
        """ To stop logging """
        self._end = True
