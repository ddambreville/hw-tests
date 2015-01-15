import pytest
import threading
import time
import subdevice


class Log(threading.Thread):

    """
    Class to log during test
    """

    def __init__(self, dcm, mem, event,  file_name):
        """
        @dcm                    : proxy to DCM (object)
        @mem                    : proxy to Motion (object)
        @event                  : event object (object)
        @file_name              : file to save log (string)
        """

        threading.Thread.__init__(self)
        self._event = event
        self._file_name = file_name

        self._robot_on_charging_station = subdevice.ChargingStationSensor(
            dcm, mem)
        self._battery_current_sensor = subdevice.BatteryChargeSensor(
            dcm, mem)
        self._wheelb_speed_act = subdevice.WheelSpeedActuator(
            dcm, mem, "WheelB")
        self._wheelfr_speed_act = subdevice.WheelSpeedActuator(
            dcm, mem, "WheelFR")
        self._wheelfl_speed_act = subdevice.WheelSpeedActuator(
            dcm, mem, "WheelFL")
        self._wheelb_speed_sen = subdevice.WheelSpeedSensor(
            dcm, mem, "WheelB")
        self._wheelfr_speed_sen = subdevice.WheelSpeedSensor(
            dcm, mem, "WheelFR")
        self._wheelfl_speed_sen = subdevice.WheelSpeedSensor(
            dcm, mem, "WheelFL")
        self._wheelb_stiffness = subdevice.WheelStiffnessActuator(
            dcm, mem, "WheelB")
        self._wheelfr_stiffness = subdevice.WheelStiffnessActuator(
            dcm, mem, "WheelFR")
        self._wheelfl_stiffness = subdevice.WheelStiffnessActuator(
            dcm, mem, "WheelFL")

        self._end = False

    def run(self):
        """ Log """

        log_file = open(self._file_name, 'w')
        line_to_write = ",".join([
            "Time",
            "Event",
            "RobotOnChargingStation",
            "BatteryCurrentSensor",
            "WheelBSpeedActuator",
            "WheelFRSpeedActuator",
            "WheelFLSpeedActuator",
            "WheelBSpeedSensor",
            "WheelFRSpeedSensor",
            "WheelFLSpeedSensor",
            "WheelBStiffness",
            "WheelFRStiffness",
            "WheelFLStiffness"
        ]) + "\n"
        log_file.write(line_to_write)
        log_file.flush()

        time_init = time.time()
        while not self._end:
            elapsed_time = time.time() - time_init

            line_to_write = ",".join([
                str(elapsed_time),
                str(self._event.flag_event),
                str(self._robot_on_charging_station.value),
                str(self._battery_current_sensor.value),
                str(self._wheelb_speed_act.value),
                str(self._wheelfr_speed_act.value),
                str(self._wheelfl_speed_act.value),
                str(self._wheelb_speed_sen.value),
                str(self._wheelfr_speed_sen.value),
                str(self._wheelfl_speed_sen.value),
                str(self._wheelb_stiffness.value),
                str(self._wheelfr_stiffness.value),
                str(self._wheelfl_stiffness.value)
            ]) + "\n"

            log_file.write(line_to_write)
            log_file.flush()

            time.sleep(0.1)

    def stop(self):
        """ To stop logging """
        self._end = True
