import pytest
import threading
import easy_plot_connection
import time
import subdevice


class MotionActuatorValue(object):

    """
    Class to get joint actuator speed value.
    """

    def __init__(self, mem, name):
        """
        @mem    : proxy to DCM (object)
        @name   : joint name (string)
        """
        self._mem = mem
        self._name = name

    def _get_value(self):
        """ Get value from ALMemory. """
        return float(self._mem.getData("Motion/Velocity/Command/" + self._name))

    value = property(_get_value)


class MotionSensorValue(object):

    """
    Class to get joint sensor speed value.
    """

    def __init__(self, mem, name):
        """
        @mem    : proxy to DCM (object)
        @name   : joint name (string)
        """
        self._mem = mem
        self._name = name

    def _get_value(self):
        """ Get value from ALMemory. """
        return float(self._mem.getData("Motion/Velocity/Sensor/" + self._name))

    value = property(_get_value)


def JointDico(dcm, mem, joint):
    """
    Return dictionnary of object (position, speed, hardness, temperature)
    for specified joint.

    @dcm        : proxy to DCM (object)
    @mem        : proxy to ALMemory (object)
    @joint      : joint name (string)
    """
    joint_pos_act = subdevice.JointPositionActuator(dcm, mem, joint)
    joint_pos_sen = subdevice.JointPositionSensor(dcm, mem, joint)
    joint_speed_act = MotionActuatorValue(mem, joint)
    joint_speed_sen = MotionSensorValue(mem, joint)
    joint_hardness = subdevice.JointHardnessActuator(dcm, mem, joint)
    joint_temp = subdevice.JointTemperature(dcm, mem, joint)

    dico_joint = {
        "PosAct": joint_pos_act,
        "PosSen": joint_pos_sen,
        "SpeedAct": joint_speed_act,
        "SpeedSen": joint_speed_sen,
        "Hardness": joint_hardness,
        "Temp": joint_temp
    }

    return dico_joint


class Plot(threading.Thread):

    """
    Class to log during test
    """

    def __init__(self, dcm, mem, event, limit_position, limit_speed, temp_max,
                 temp_max_to_start, file_name):
        """
        @dcm                    : proxy to DCM (object)
        @mem                    : proxy to Motion (object)
        @event                  : event object (object)
        @limit_position         : limit position (integer)
        @limit_speed            : limit speed (integer)
        @temp_max               : maximal joint temperature permitted (integer)
        @temp_max_to_start      : maximal joint temperature permitted to start
                                  (integer)
        @file_name              : file to save log (string)
        """

        threading.Thread.__init__(self)
        self._mem = mem
        self._event = event
        self._limit_position = limit_position
        self._limit_speed = limit_speed
        self._temp_max = temp_max
        self._temp_max_to_start = temp_max_to_start
        self._file_name = file_name

        self._dico = {
            "RShoulderPitch": JointDico(dcm, mem, "RShoulderPitch"),
            "LShoulderPitch": JointDico(dcm, mem, "LShoulderPitch"),
            "RShoulderRoll": JointDico(dcm, mem, "RShoulderRoll"),
            "LShoulderRoll": JointDico(dcm, mem, "LShoulderRoll"),
            "RElbowRoll": JointDico(dcm, mem, "RElbowRoll"),
            "LElbowRoll": JointDico(dcm, mem, "LElbowRoll"),
            "RElbowYaw": JointDico(dcm, mem, "RElbowYaw"),
            "LElbowYaw": JointDico(dcm, mem, "LElbowYaw")
        }

        self._end = False

    def run(self):
        """ Log """

        plot_server = easy_plot_connection.Server(local_plot=True)
        plot_server.curves_erase()

        time_init = time.time()
        while not self._end:
            elapsed_time = time.time() - time_init
            for key, value in self._dico.items():
                plot_server.add_point(
                    key + "ErrorPos",
                    elapsed_time,
                    value["PosAct"].value - value["PosSen"].value
                )
                plot_server.add_point(
                    key + "ErrorSpeed",
                    elapsed_time,
                    value["SpeedAct"].value - value["SpeedSen"].value
                )
                plot_server.add_point(
                    key + "Hardness",
                    elapsed_time,
                    value["Hardness"].value
                )
            plot_server.add_point(
                "RShoulderRollTemp",
                elapsed_time,
                self._dico["RShoulderRoll"]["Temp"]
            )
            plot_server.add_point(
                "LShoulderRollTemp",
                elapsed_time,
                self._dico["LShoulderRoll"]["Temp"]
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
                "TemperatureMin",
                elapsed_time,
                self._temp_max_to_start
            )
            plot_server.add_point(
                "TemperatureMax",
                elapsed_time,
                self._temp_max
            )

            time.sleep(0.1)

        plot_server.stop()

    def stop(self):
        """ To stop logging """
        self._end=True
