import pytest
import threading
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


class Log(threading.Thread):

    """
    Class to log during test
    """

    def __init__(self, dcm, mem, event, pushrecovery, limit_position,
                 limit_speed, temp_max, temp_max_to_start, file_name):
        """
        @dcm                    : proxy to DCM (object)
        @mem                    : proxy to Motion (object)
        @event                  : event object (object)
        @pushrecovery           : pushrecovery event object (object)
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
        self._pushrecovery = pushrecovery
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

        log_file = open(self._file_name, 'w')
        line_to_write = ",".join([
            "Time",
            "Event",
            "EventType",
            "PushRecovery",
            "TemperatureMin",
            "TemperatureMax",
            "MaxLimitErrorPosition",
            "MinLimitErrorPosition",
            "MaxLimitErrorSpeed",
            "MinLimitErrorSpeed",
            "RShoulderPitchErrorPos",
            "LShoulderPitchErrorPos",
            "RShoulderRollErrorPos",
            "LShoulderRollErrorPos",
            "RElbowRollErrorPos",
            "LElbowRollErrorPos",
            "RElbowYawErrorPos",
            "LElbowYawErrorPos",
            "RShoulderPitchErrorSpeed",
            "LShoulderPitchErrorSpeed",
            "RShoulderRollErrorSpeed",
            "LShoulderRollErrorSpeed",
            "RElbowRollErrorSpeed",
            "LElbowRollErrorSpeed",
            "RElbowYawErrorSpeed",
            "LElbowYawErrorSpeed",
            "RShoulderPitchHardness",
            "LShoulderPitchHardness",
            "RShoulderRollHardness",
            "LShoulderRollHardness",
            "RElbowRollHardness",
            "LElbowRollHardness",
            "RElbowYawHardness",
            "LElbowYawHardness",
            "RShoulderRollTemp",
            "LShoulderRollTemp"
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
                str(self._pushrecovery.flag),
                str(self._temp_max_to_start),
                str(self._temp_max),
                str(self._limit_position),
                str(-self._limit_position),
                str(self._limit_speed),
                str(-self._limit_speed)
            ]) + ","
            # Error if do in one time...
            line_to_write += ",".join([
                str(x["PosAct"].value -
                    x["PosSen"].value) for x in self._dico.values()
            ]) + ","
            line_to_write += ",".join([
                str(y["SpeedAct"].value -
                    y["SpeedSen"].value) for y in self._dico.values()
            ]) + ","
            line_to_write += ",".join([
                str(z["Hardness"].value) for z in self._dico.values()
            ]) + ","
            line_to_write += ",".join([
                str(self._dico["RShoulderRoll"]["Temp"].value),
                str(self._dico["RShoulderRoll"]["Temp"].value)
            ]) + "\n"

            log_file.write(line_to_write)
            log_file.flush()

            time.sleep(0.1)

    def stop(self):
        """ To stop logging """
        self._end = True
