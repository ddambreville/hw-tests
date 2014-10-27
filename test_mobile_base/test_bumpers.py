import pytest
import tools
import subdevice
import threading
import time
import sys
import math
import random
import mobile_base_utils
from naoqi import ALProxy


SHOULDER_LEDS = [
"ChestBoard/Led/Red/Actuator/Value",
"ChestBoard/Led/Green/Actuator/Value",
"ChestBoard/Led/Blue/Actuator/Value"
]


def stiff_wheels(list_wheel_stiffness): 
    """
    Stiff the 3 wheels
    """
    for stiffness in list_wheel_stiffness:
        stiffness.qvalue = (1.0, 0)


def unstiff_wheels(list_wheel_stiffness): 
    """
    Unstiff the 3 wheels
    """
    for stiffness in list_wheel_stiffness:
        stiffness.qvalue = (0.0, 0)


def stop_robot(list_wheel_speed):
    """
    Stop the robot
    """
    print "hello"
    for speed in list_wheel_speed:
        speed.qvalue = (0.0, 0)


def check_wheel_temperatures(dcm, leds, list_wheel_temperature, list_wheel_speed, list_wheel_stiffness):
    """
    Pauses the robot if the wheels are too hot
    """
    if list_wheel_temperature[0].value >= 80 or \
       list_wheel_temperature[1].value >= 80 or \
       list_wheel_temperature[2].value >= 80:

        print("\nWheels too hot --> Waiting")
        leds.fadeListRGB("shoulder_group", [0x00FF00FF,], [0.,])
        stop_robot(list_wheel_speed)
        unstiff_wheels(list_wheel_stiffness)

        # Wait 
        while list_wheel_temperature[0].value >= 45 or \
              list_wheel_temperature[1].value >= 45 or \
              list_wheel_temperature[2].value >= 45:
            tools.wait(dcm, 20000)

        leds.reset("shoulder_group")
        stiff_wheels(list_wheel_stiffness)


def move_robot_random(dcm, mem, wait_time, min_fraction, max_fraction, max_random):
    """
    Makes the robot move randomly.
    """

    #---------------------------------------------------------#
    #-------------------- Object creations -------------------#
    #---------------------------------------------------------#

    # Wheel speed actuators
    wheel_fr_speed_actuator = subdevice.WheelSpeedActuator(
        dcm, mem, "WheelFR")
    wheel_fl_speed_actuator = subdevice.WheelSpeedActuator(
        dcm, mem, "WheelFL")
    wheel_b_speed_actuator  = subdevice.WheelSpeedActuator(
        dcm, mem, "WheelB")

    # Random speed
    speed_fraction_fr = float(format(random.uniform(min_fraction, max_fraction), '.1f'))
    speed_fraction_fl = float(format(random.uniform(min_fraction, max_fraction), '.1f'))
    speed_fraction_b  = float(format(random.uniform(min_fraction, max_fraction), '.1f'))

    print type(speed_fraction_fr)
    print type(speed_fraction_fl)
    print type(speed_fraction_b)

    speed_fr = speed_fraction_fr * wheel_fr_speed_actuator.maximum
    speed_fl = speed_fraction_fl * wheel_fl_speed_actuator.maximum
    speed_b  = speed_fraction_b  * wheel_b_speed_actuator.maximum

    alea = int(random.uniform(0, 15))

    # Make the robot move randomly
    #-------------------------- CASE 1 -------------------------#
    if alea <= 5:
        timed_commands_fr = [(-speed_fr, wait_time)]
        timed_commands_fl = [(speed_fl, wait_time)]
        timed_commands_b  = [(0.0, wait_time)]

        wheel_fr_speed_actuator.mqvalue = timed_commands_fr
        wheel_fl_speed_actuator.mqvalue = timed_commands_fl

        return [timed_commands_fr, timed_commands_fl, timed_commands_b]

    #-------------------------- CASE 2 -------------------------#
    if alea > 5 and alea <= 10:
        timed_commands_fl = [(-speed_fl, wait_time)]
        timed_commands_b  = [(speed_b, wait_time)]
        timed_commands_fr = [(0.0, wait_time)]

        wheel_fl_speed_actuator.mqvalue = timed_commands_fl
        wheel_b_speed_actuator.mqvalue  = timed_commands_b

        return [timed_commands_fr, timed_commands_fl, timed_commands_b]

    #-------------------------- CASE 3 -------------------------#
    if alea > 10 and alea <= 15:
        timed_commands_b  = [(-speed_b, wait_time)]
        timed_commands_fr = [(speed_fr, wait_time)]
        timed_commands_fl = [(0.0, wait_time)]

        wheel_b_speed_actuator.mqvalue  = timed_commands_b
        wheel_fr_speed_actuator.mqvalue = timed_commands_fr

        return [timed_commands_fr, timed_commands_fl, timed_commands_b]


def test_move_random(dcm, mem, leds, expressiveness, wait_time, wait_time_bumpers, 
                     min_fraction, max_fraction, max_random, 
                     stop_robot, wake_up_pos_brakes_closed, 
                     stiff_robot_wheels, unstiff_joints, 
                     log_wheels_speed, log_bumper_pressions):

    #---------------------------------------------------------#
    #-------------------- Object creations -------------------#
    #---------------------------------------------------------#

    #------------------------- Wheels ------------------------#

    list_wheel_speed_actuator = [
        subdevice.WheelSpeedActuator(dcm, mem, "WheelFR"),
        subdevice.WheelSpeedActuator(dcm, mem, "WheelFL"),
        subdevice.WheelSpeedActuator(dcm, mem, "WheelB")
    ]

    list_wheel_speed_sensor = [
        subdevice.WheelSpeedSensor(dcm, mem, "WheelFR"),
        subdevice.WheelSpeedSensor(dcm, mem, "WheelFL"),
        subdevice.WheelSpeedSensor(dcm, mem, "WheelB")
    ]

    list_wheel_stiffness_actuator = [
        subdevice.WheelStiffnessActuator(dcm, mem, "WheelFR"),
        subdevice.WheelStiffnessActuator(dcm, mem, "WheelFL"),
        subdevice.WheelStiffnessActuator(dcm, mem, "WheelB")
    ]

    list_wheel_temperature = [
        subdevice.WheelTemperatureSensor(dcm, mem, "WheelFR"),
        subdevice.WheelTemperatureSensor(dcm, mem, "WheelFL"),
        subdevice.WheelTemperatureSensor(dcm, mem, "WheelB")
    ]

    #------------------------- Bumpers -----------------------#

    list_bumper = [
        subdevice.Bumper(dcm, mem, "FrontRight"),
        subdevice.Bumper(dcm, mem, "FrontLeft"),
        subdevice.Bumper(dcm, mem, "Back")
    ]

    #-------------------------- Leds --------------------------#

    # Disable notifications (from disconnected tablet)
    expressiveness._setNotificationEnabled(False)

    # Switch off eyes and ears leds
    leds.off('FaceLeds')
    leds.off('EarLeds')

    # Switch on shoulder leds
    leds.createGroup("shoulder_group", SHOULDER_LEDS)
    leds.on("shoulder_group")

    # Bumpers activation detection 
    parameters_bumpers = tools.read_section("config.cfg", "BumpersActivationsParameters")

    # Launch bumper counter (thread)
    bumper_detection = mobile_base_utils.BumpersCounting(dcm, mem, leds,
        wait_time_bumpers)
    bumper_detection.start()

    #---------------------------------------------------------#
    #--------------------- Initialization --------------------#
    #---------------------------------------------------------#
    flag_bumpers = False
    list_commands = move_robot_random(dcm, mem, wait_time, min_fraction, max_fraction, max_random)
    tools.wait(dcm, 2000)

    #---------------------------------------------------------#
    #----------------------- Main Loop -----------------------#
    #---------------------------------------------------------#
    while flag_bumpers == False:

        try: 
            #-------------------- Wall event -------------------#
            if (list_bumper[0].value == 1) or \
               (list_bumper[1].value == 1) or \
               (list_bumper[2].value == 1):

                # Robot hit wall --> Stop it
                list_wheel_speed_actuator[0].qvalue = (0.0, 0)
                list_wheel_speed_actuator[1].qvalue = (0.0, 0)
                list_wheel_speed_actuator[2].qvalue = (0.0, 0)

                # Going back
                list_wheel_speed_actuator[0].qvalue = [ (-1) * list_commands[0][0][0], wait_time]
                list_wheel_speed_actuator[1].qvalue = [ (-1) * list_commands[1][0][0], wait_time]
                list_wheel_speed_actuator[2].qvalue = [ (-1) * list_commands[2][0][0], wait_time]

                tools.wait(dcm, 4000)

                # random again
                list_commands = move_robot_random(dcm, mem, wait_time, min_fraction, max_fraction, max_random)

                #tools.wait(dcm, 2000)


            #--------------------- Check temperatures --------------------#
            check_wheel_temperatures(dcm, leds, list_wheel_temperature, 
                list_wheel_speed_actuator, list_wheel_stiffness_actuator)


            #-------------------- Check test variables -------------------#
            if bumper_detection.bumpers_activations == \
                    int(parameters_bumpers["nb_bumper_activations"][0]):
                bumper_detection.stop()
                flag_bumpers = True


        # Exit test if user interrupt
        except KeyboardInterrupt:
                print "\n******* User interrupt - ending test *******"
                bumper_detection.stop()
                break