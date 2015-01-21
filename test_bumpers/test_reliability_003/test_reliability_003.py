import pytest
import qha_tools
import subdevice
import threading
import time
import uuid


class Log(threading.Thread):

    """
    Class to log during test
    """

    def __init__(self, dcm, mem, file_name):
        """
        @dcm                    : proxy to DCM (object)
        @mem                    : proxy to ALMemory (object)
        @file_name              : name of log file (string)
        """

        threading.Thread.__init__(self)
        self._mem = mem
        self._file_name = file_name

        self._wheelb_speed_act = subdevice.WheelSpeedActuator(
            dcm, mem, "WheelB")
        self._wheelfr_speed_act = subdevice.WheelSpeedActuator(
            dcm, mem, "WheelFR")
        self._wheelfl_speed_act = subdevice.WheelSpeedActuator(
            dcm, mem, "WheelFL")
        self._rightbumper = subdevice.Bumper(dcm, mem, "FrontRight")
        self._leftbumper = subdevice.Bumper(dcm, mem, "FrontLeft")

        self._end = False

    def run(self):
        """ Log datas"""

        log_file = open(self._file_name + ".csv", 'w')
        line_to_write = ",".join([
            "Time",
            "RightBumper",
            "LeftBumper",
            "WheelBSpeedAct",
            "WheelFRSpeedAct",
            "WheelFLSpeedAct"
        ]) + "\n"
        log_file.write(line_to_write)
        log_file.flush()

        time_init = time.time()
        while not self._end:
            elapsed_time = time.time() - time_init
            line_to_write = ",".join([
                str(elapsed_time),
                str(self._rightbumper.value),
                str(self._leftbumper.value),
                str(self._wheelb_speed_act.value),
                str(self._wheelfr_speed_act.value),
                str(self._wheelfl_speed_act.value)
            ]) + "\n"
            log_file.write(line_to_write)
            log_file.flush()

            time.sleep(0.1)

    def stop(self):
        """ To stop logging """
        self._end = True


def move(motion, speed, direction):
    motion.move(speed * int(direction["x"][0]),
                speed * int(direction["y"][0]),
                speed * int(direction["z"][0])
                )


def moveto(motion, distance, direction):
    motion.moveTo(-distance * int(direction["x"][0]),
                  -distance * int(direction["y"][0]),
                  -distance * int(direction["z"][0])
                  )


def test_reliability_003(dcm, mem, motion, motion_wake_up, parameters,
                         direction):
    """
    Test : bumper detects step.
    Return True if bumper detects obstacles and robot stops
    Return False if bumper detects obstacle but robot moves again

    @dcm                : proxy to DCM (object)
    @mem                : proxy to ALMemory (object)
    @motion             : proxy to ALMotion (object)
    @motion_wake_up     : robot does it wakeUp
    @parameters         : dictionnary {"parameter":value} from config file
                            (dictionnary)
    @directions         : dictionnary {"direction":value} (dictionnary)
    """
    # Objects creation
    right_bumper = subdevice.Bumper(dcm, mem, "FrontRight")
    left_bumper = subdevice.Bumper(dcm, mem, "FrontLeft")
    back_bumper = subdevice.Bumper(dcm, mem, "Back")
    wheelfr_speed_act = subdevice.WheelSpeedActuator(
        dcm, mem, "WheelFR")
    wheelfl_speed_act = subdevice.WheelSpeedActuator(
        dcm, mem, "WheelFL")

    log = Log(dcm, mem, direction + "-" + parameters["Speed"][0])
    log.start()

    print "Go move"
    move(motion, float(parameters["Speed"][0]),
         qha_tools.read_section("reliability_003.cfg", "Direction" + direction)
         )
    print "Move finish"

    flag = 0
    while flag < int(parameters["Nbcycles"][0]):
        if right_bumper.value or left_bumper.value or back_bumper.value:
            print "Bumper"
            time.sleep(3)  # Time to wait wheel actuators reaction...
            if wheelfr_speed_act.value == 0 and wheelfl_speed_act.value == 0:
                print "Stop OK"
                flag += 1
                time.sleep(5)   # Robot forget mapping
                moveto(motion, float(parameters["MoveBackDistance"][0]),
                       qha_tools.read_section(
                           "reliability_003.cfg", "Direction" + direction)
                       )
                print "Move back OK"
                time.sleep(2)
                move(motion, float(parameters["Speed"][0]),
                     qha_tools.read_section(
                         "reliability_003.cfg", "Direction" + direction)
                     )
                print "Move"
            else:
                print flag
                break

    log.stop()

    assert flag == int(parameters["Nbcycles"][0])
