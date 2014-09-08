import pytest
import tools
import subdevice
import threading
import time
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

        self.arms = tools.use_section("arms.cfg", "arms")

        self.cyling_flag = 0   # 0:kneepitch, 1:hippitch, 2:hiproll

    def unstiff_arms(self):
        for name in self.arms:
            print(name)
            joint_hardness = subdevice.JointHardnessActuator(
                self.dcm, self.mem, name)
            joint_hardness.qqvalue = 0.

    def cycling(self):
        self.unstiff_arms()
        while True:
            if self.cyling_flag == 0:
                print "KneePitch cycling"
                self.kneepitch_cycling()
            elif self.cyling_flag == 1:
                print "HipPitch cycling"
                self.hippitch_cycling()
            else:
                print "HipRoll cycling"
                self.hiproll_cycling()

    def kneepitch_cycling(self):
        """ KneePitch cycling"""
        # Initial position
        self.hippitch_position_actuator.qvalue = (0., 3000)
        self.hiproll_position_actuator.qvalue = (0., 3000)
        tools.wait(self.dcm, 3100)
        self.hippitch_hardness_actuator.qqvalue = 0.
        
        while self.kneepitch_temperature.value < 60:
            self.kneepitch_position_actuator.qvalue = (-0.2, 2000)
            tools.wait(self.dcm, 2100)
            self.kneepitch_position_actuator.qvalue = (0.2, 1000)
            tools.wait(self.dcm, 1100)
            print(str(self.kneepitch_temperature.value))

            if abs(self.hippitch_position_actuator.value -\
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

        while self.hippitch_temperature.value < 60:
            self.hippitch_position_actuator.qvalue = (0.3, 2000)
            tools.wait(self.dcm, 2100)
            self.hippitch_position_actuator.qvalue = (-0.3, 1000)
            tools.wait(self.dcm, 1100)
            print(str(self.hippitch_temperature.value))

            if abs(self.kneepitch_position_actuator.value -\
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

        while self.hiproll_temperature.value < 60:
            self.hiproll_position_actuator.qvalue = (0.5, 1000)
            tools.wait(self.dcm, 1100)
            self.hiproll_position_actuator.qvalue = (-0.5, 1000)
            tools.wait(self.dcm, 1100)
            print(str(self.hiproll_temperature.value))

            if abs(self.hippitch_position_actuator.value -\
                   self.hippitch_position_sensor.value) > math.radians(5.) or\
                   (self.kneepitch_position_actuator.value -\
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


def test_pod_damage(dcm, mem, wake_up_pos, rest_pos, kill_motion, stiff_robot):
    # Objects creation
    robot_on_charging_station = subdevice.ChargingStationSensor(dcm, mem)
    battery_current = subdevice.BatteryCurrentSensor(dcm, mem)
    logger = tools.Logger()

    # Going to initial position
    subdevice.multiple_set(dcm, mem, wake_up_pos, wait=True)

    # Flag initialization
    flag = True

    test_pod = PodTest(dcm, mem)

    my_behavior = threading.Thread(target=test_pod.cycling())
    my_behavior.start()

    # Timer creation just before test loop
    timer = tools.Timer(dcm, 100000)

    while timer.is_time_not_out():
        logger.log(
            ("Time", timer.dcm_time() / 1000.),
            ("RobotOnChargingStation", robot_on_charging_station.value),
            ("BatteryCurrent", battery_current.value)
        )

    logger.log_file_write("test_pod.csv")

    assert flag
