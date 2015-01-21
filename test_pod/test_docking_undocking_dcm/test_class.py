# -*- coding: utf-8 -*-

'''
Created on January 14, 2015

@author: amartin
'''

import qha_tools
import subdevice
import time
import threading
import sys


class TestPodDCM(object):

    '''
    Class test Pod with DCM
    '''

    def __init__(self, dcm, mem):
        """
        Initialisation de la class
        """
        self.dcm = dcm
        self.mem = mem
        self.parameters = qha_tools.read_section(
            "test_config.cfg", "DockCyclingParameters")
        self.wheel_motion = subdevice.WheelsMotion(
            self.dcm, self.mem, float(self.parameters["speed"][0]))
        self.robot_on_charging_station = subdevice.ChargingStationSensor(
            self.dcm, self.mem)
        self.wheelfr_temperature_sensor = subdevice.WheelTemperatureSensor(
            self.dcm, self.mem, "WheelFR")
        self.wheelfl_temperature_sensor = subdevice.WheelTemperatureSensor(
            self.dcm, self.mem, "WheelFL")
        self.wheelb_temperature_sensor = subdevice.WheelTemperatureSensor(
            self.dcm, self.mem, "WheelB")
        self.back_bumper_sensor = subdevice.Bumper(dcm, mem, "Back")
        self.battery_current = subdevice.BatteryCurrentSensor(
            self.dcm, self.mem)
        self.nb_cycles = self.parameters["nb_cycles"][0]
        self.log_file = open(self.parameters["cycling_cvs_name"][0], 'w')
        self.check_temperature_thread = threading.Thread(
            target=self._check_temperature_thread, args=())
        self.check_temperature = None
        self.wheel_hot = None

    def initialisation(self):
        '''
        Init state
        '''
        self.remove_stiffness()
        if self.robot_on_charging_station.value == 0:
            print "Put the robot on the pod\n"
            # assert False
        self.log_file.write(
            "Cycle,Connection,BatteryCurrent\n")
        self.check_temperature = True
        self.wheel_hot = False
        self.check_temperature_thread.start()

    def _check_temperature_thread(self):
        '''
        Check wheel temperature thread
        '''
        while self.check_temperature == True:
            wheels_temp = [self.wheelfr_temperature_sensor.value,
                           self.wheelfl_temperature_sensor.value,
                           self.wheelb_temperature_sensor.value]
            if max(wheels_temp) > float(self.parameters[
                    "wheels_temperature_limit"][0]):
                self.wheel_hot = True
                time.sleep(1)
            if self.wheel_hot == True:
                sys.stdout.write(
                    "Wheel temperature is too hot : " + str(max(wheels_temp)) +
                    "°C . Wait..." + chr(13))
                sys.stdout.flush()
            if max(wheels_temp) < float(self.parameters[
                    "wheels_temperature_cooling"][0]):
                self.wheel_hot = False

    def move_robot_x(self, side):
        '''
        Move robot along X axis
        '''
        if side == 'Back':
            self.wheel_motion.move_x(
                float(self.parameters["distance_back"][0]))
        if side == 'Front':
            self.wheel_motion.move_x(
                float(self.parameters["distance_front"][0]))
            time.sleep(0.5)

    def remove_stiffness(self):
        '''
        Remove wheels stiffness
        '''
        self.wheel_motion.stiff_wheels(
            ["WheelFR", "WheelFL", "WheelB"], 0.0)

    def check_connection(self, cycle):
        '''
        Check POD connection
        '''
        time.sleep(float(self.parameters["time_wait_on_the_pod"][0]))
        line_to_write = ",".join([
            str(cycle),
            str(int(self.robot_on_charging_station.value)),
            str(float(self.battery_current.value))
        ])
        line_to_write += "\n"
        self.log_file.write(line_to_write)
        self.log_file.flush()

    def end(self):
        '''
        End State
        '''
        self.check_temperature = False
        self.remove_stiffness()
