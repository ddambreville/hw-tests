import pytest
import tools
import subdevice
import threading
import math


class PodTest(object):

    def __init__(self, dcm, mem):
        self.dcm = dcm
        self.mem = mem
        self.kneepitch_position_actuator = subdevice.JointPositionActuator(
            dcm, mem, "KneePitch")
        self.kneepitch_position_sensor = subdevice.JointPositionSensor(
            dcm, mem, "KneePitch")
        self.kneepitch_hardness_actuator = subdevice.JointHardnessActuator(
            dcm, mem, "KneePitch")
        self.kneepitch_temperature = subdevice.JointTemperature(
            dcm, mem, "KneePitch")
        self.hippitch_position_actuator = subdevice.JointPositionActuator(
            dcm, mem, "HipPitch")
        self.hippitch_position_sensor = subdevice.JointPositionSensor(
            dcm, mem, "HipPitch")
        self.hippitch_hardness_actuator = subdevice.JointHardnessActuator(
            dcm, mem, "HipPitch")
        self.hippitch_temperature = subdevice.JointTemperature(
            dcm, mem, "HipPitch")
        self.hiproll_position_actuator = subdevice.JointPositionActuator(
            dcm, mem, "HipRoll")
        self.hiproll_temperature = subdevice.JointTemperature(
            dcm, mem, "HipRoll")

        self.cyling_flag = 0   # 0:kneepitch, 1:hippitch, 2:hiproll
        self.cycling_step = 0
        self._cycling_stop_flag = True

        self._stop_cycling = False

    def unstiff_parts(self, section):
        joints = tools.use_section("parts.cfg", section)
        for name in joints:
            # print(name)
            joint_hardness = subdevice.JointHardnessActuator(
                self.dcm, self.mem, name)
            joint_hardness.qqvalue = 0.

    def increase_cycling_step(self):
        """ To stop test timer if robot too hot and can't move"""
        if self.cycling_step < 3:
            self.cycling_step += 1
        else:
            self._set_cycling_stop_flag(True)
            tools.wait(self.dcm, 20000)

    def cycling(self):
        while self._stop_cycling == False:
            if self.cyling_flag == 0:
                print(str(self.cycling_step))
                if self.kneepitch_temperature.value < 60:
                    print "KneePitch cycling"
                    self.cycling_step = 0
                    self._set_cycling_stop_flag(False)
                    self.kneepitch_cycling()
                else:
                    self.increase_cycling_step()
                self.cyling_flag = 1
            elif self.cyling_flag == 1:
                print(str(self.cycling_step))
                if self.hippitch_temperature.value < 60:
                    print "HipPitch cycling"
                    self.cycling_step = 0
                    self._set_cycling_stop_flag(False)
                    self.hippitch_cycling()
                else:
                    self.increase_cycling_step()
                self.cyling_flag = 2
            else:
                print(str(self.cycling_step))
                if self.hiproll_temperature.value < 60:
                    print "HipRoll cycling"
                    self.cycling_step = 0
                    self._set_cycling_stop_flag(False)
                    self.hiproll_cycling()
                else:
                    self.increase_cycling_step()
                self.cyling_flag = 0

    def kneepitch_cycling(self):
        """ KneePitch cycling"""
        # Initial position
        self.hippitch_position_actuator.qvalue = (0., 3000)
        self.hiproll_position_actuator.qvalue = (0., 3000)
        tools.wait(self.dcm, 3100)
        self.hippitch_hardness_actuator.qqvalue = 0.

        while self.kneepitch_temperature.value < 60 and\
                self._stop_cycling == False:
            self.kneepitch_position_actuator.qvalue = (-0.2, 2000)
            tools.wait(self.dcm, 2100)
            self.kneepitch_position_actuator.qvalue = (0.2, 2000)
            tools.wait(self.dcm, 2100)
            print(str(self.kneepitch_temperature.value))

            if abs(self.hippitch_position_actuator.value -
                   self.hippitch_position_sensor.value) > math.radians(5.):
                print "Error"
                self.kneepitch_position_actuator.qvalue = (0., 2000)
                tools.wait(self.dcm, 2100)
                self.hippitch_hardness_actuator.qqvalue = 1.
                self.hippitch_position_actuator.qvalue = (0., 1000)
                tools.wait(self.dcm, 1100)
                self.hippitch_hardness_actuator.qqvalue = 0.

        self.cyling_flag = 1
        self.kneepitch_position_actuator.qvalue = (0., 3000)
        tools.wait(self.dcm, 3100)
        self.hippitch_hardness_actuator.qqvalue = 1.

    def hippitch_cycling(self):
        """ HipPitch cycling"""
        # Initial position
        self.kneepitch_position_actuator.qvalue = (0., 3000)
        self.hiproll_position_actuator.qvalue = (0., 3000)
        tools.wait(self.dcm, 3100)
        self.kneepitch_hardness_actuator.qqvalue = 0.

        while self.hippitch_temperature.value < 60 and\
                self._stop_cycling == False:
            self.hippitch_position_actuator.qvalue = (0.3, 2000)
            tools.wait(self.dcm, 2100)
            self.hippitch_position_actuator.qvalue = (-0.3, 1000)
            tools.wait(self.dcm, 1100)
            print(str(self.hippitch_temperature.value))

            if abs(self.kneepitch_position_actuator.value -
                   self.kneepitch_position_sensor.value) > math.radians(5.):
                self.hippitch_position_actuator.qvalue = (0., 2000)
                tools.wait(self.dcm, 2100)
                self.kneepitch_hardness_actuator.qqvalue = 1.
                self.kneepitch_position_actuator.qvalue = (0., 1000)
                tools.wait(self.dcm, 1100)
                self.kneepitch_hardness_actuator.qqvalue = 0.

        self.cyling_flag = 2
        self.hippitch_position_actuator.qvalue = (0., 3000)
        tools.wait(self.dcm, 3100)
        self.kneepitch_hardness_actuator.qqvalue = 1.

    def hiproll_cycling(self):
        """HipRoll cycling"""
        # Initial position
        self.kneepitch_position_actuator.qvalue = (0., 3000)
        tools.wait(self.dcm, 3100)
        self.hippitch_position_actuator.qvalue = (0., 3000)
        tools.wait(self.dcm, 3100)
        self.kneepitch_hardness_actuator.qqvalue = 0.
        self.hippitch_hardness_actuator.qqvalue = 0.

        while self.hiproll_temperature.value < 60 and\
                self._stop_cycling == False:
            self.hiproll_position_actuator.qvalue = (0.5, 1000)
            tools.wait(self.dcm, 1100)
            self.hiproll_position_actuator.qvalue = (-0.5, 1000)
            tools.wait(self.dcm, 1100)
            print(str(self.hiproll_temperature.value))

            if abs(self.hippitch_position_actuator.value -
                   self.hippitch_position_sensor.value) > math.radians(5.) or\
                  (self.kneepitch_position_actuator.value -
                   self.kneepitch_position_sensor.value) > math.radians(5.):
                self.hiproll_position_actuator.qvalue = (0., 1000)
                tools.wait(self.dcm, 1100)
                self.hippitch_hardness_actuator.qqvalue = 1.
                self.hippitch_position_actuator.qvalue = (0., 2000)
                tools.wait(self.dcm, 2100)
                self.hippitch_hardness_actuator.qqvalue = 0.
                self.kneepitch_hardness_actuator.qqvalue = 1.
                self.kneepitch_position_actuator.qvalue = (0., 2000)
                tools.wait(self.dcm, 2100)
                self.kneepitch_hardness_actuator.qqvalue = 0.

        self.cyling_flag = 0
        self.hiproll_position_actuator.qvalue = (0., 3000)
        tools.wait(self.dcm, 3100)
        self.kneepitch_hardness_actuator.qqvalue = 1.
        self.hippitch_hardness_actuator.qqvalue = 1.

    def _get_cycling_stop_flag(self):
        return self._cycling_stop_flag

    def _set_cycling_stop_flag(self, status):
        self._cycling_stop_flag = bool(status)

    def _get_stop_cycling(self):
        return self._stop_cycling

    def _set_stop_cycling(self, status):
        self._stop_cycling = bool(status)

    cycling_stop_flag = property(
        _get_cycling_stop_flag, _set_cycling_stop_flag)
    stop_cycling = property(_get_stop_cycling, _set_stop_cycling)


def test_pod_damage(dcm, mem, wake_up_pos, kill_motion, stiff_robot, test_time):
    # Objects creation
    robot_on_charging_station = subdevice.ChargingStationSensor(dcm, mem)
    battery_current = subdevice.BatteryCurrentSensor(dcm, mem)
    logger = tools.Logger()

    pod = PodTest(dcm, mem)
    pod.unstiff_parts("head")
    pod.unstiff_parts("arms")

    # Going to initial position
    subdevice.multiple_set(dcm, mem, wake_up_pos, wait=True)

    # Flag initialization
    flag = True

    my_behavior = threading.Thread(target=pod.cycling)
    my_behavior.start()

    # Timer creation just before test loop
    timer = tools.Timer(dcm, test_time * 1000)
    test_timer = 0.
    time_delete = 0.
    while timer.is_time_not_out():
        # Si cyclage, log des donnees
        if pod.cycling_stop_flag == False:
            test_timer = timer.dcm_time() - time_delete
            logger.log(
                ("Time", test_timer / 1000.),
                ("RobotOnChargingStation", robot_on_charging_station.value),
                ("BatteryCurrent", battery_current.value)
            )

        # Si arret, non log des donnees
        else:
            # print "Test en pause"
            time_delete = timer.dcm_time() - test_timer
            #print("Test_delete = " + str(time_delete / 1000))

    pod.stop_cycling = True
    print("Robot moved during " + str(test_timer / 1000) + " seconds\n")
    logger.log_file_write("test_pod.csv")

    assert flag
