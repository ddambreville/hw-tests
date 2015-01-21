# -*- coding: utf-8 -*-

'''
Created on January 14, 2015

@author: amartin
'''

import qha_tools
import subdevice
import time


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
        self.back_bumper_sensor = subdevice.Bumper(dcm, mem, "Back")
        self.battery_current = subdevice.BatteryCurrentSensor(
            self.dcm, self.mem)
        self.nb_cycles = self.parameters["nb_cycles"][0]
        self.log_file = open(self.parameters["cycling_cvs_name"][0], 'w')

    def initialisation(self):
        '''
        Init state
        '''
        self.remove_stiffness()
        if self.robot_on_charging_station.value == 0:
            print "Put the robot on the pod\n"
            # assert False
        self.log_file.write(
            "Cycle,Connection, BatteryCurrent\n")

    def move_robot_x(self, side):
        '''
        Docstring
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
        Docstring
        '''
        self.wheel_motion.stiff_wheels(
            ["WheelFR", "WheelFL", "WheelB"], 0.0)

    def check_connection(self, cycle):
        '''
        Docstring
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
        Docstring
        '''
        self.remove_stiffness()
