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
        """ Log """

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


def test_reliability_003(dcm, mem, motion, session, remove_sensors,
                         motion_wake_up, parameters):
    """
    Docstring
    """
    # Objects creation
    right_bumper = subdevice.Bumper(dcm, mem, "FrontRight")
    left_bumper = subdevice.Bumper(dcm, mem, "FrontLeft")
    wheelfr_speed_act = subdevice.WheelSpeedActuator(
        dcm, mem, "WheelFR")
    wheelfl_speed_act = subdevice.WheelSpeedActuator(
        dcm, mem, "WheelFL")

    # motion.setEnableNotifications(0)

    log = Log(dcm, mem, parameters["FileName"][0])
    log.start()

    motion.move(float(parameters["Speed"][0]), 0, 0)

    flag = 0
    while flag < int(parameters["Nbcycles"][0]):
        if right_bumper.value or left_bumper.value:
            print "Bumper"
            time.sleep(3)  # Time to wait wheel actuators reaction...
            if wheelfr_speed_act.value == 0 and wheelfl_speed_act.value == 0:
                print "Stop OK"
                flag += 1
                time.sleep(5)   # Robot forget mapping
                motion.moveTo(-float(parameters["MoveBackDistance"][0]), 0, 0)
                print "Move back OK"
                time.sleep(2)
                motion.move(float(parameters["Speed"][0]), 0, 0)
                print "Move"
            else:
                print flag
                break

    log.stop()

    assert flag == int(parameters["Nbcycles"][0])
