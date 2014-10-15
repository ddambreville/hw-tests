import pytest
import tools
import subdevice
import threading
import time
import math
import random
import mobile_base_utils
from naoqi import ALProxy


SHOULDER_LEDS=[
"ChestBoard/Led/Red/Actuator/Value",
"ChestBoard/Led/Green/Actuator/Value",
"ChestBoard/Led/Blue/Actuator/Value"
]


def move_random(dcm, mem, wait_time, min_fraction, max_fraction, max_random):
    """
    Makes the robot move randomly
    """

    #---------------------------------------------------------#
    #-------------------- Object creations -------------------#
    #---------------------------------------------------------#

    wheel_fr_speed_actuator = subdevice.WheelSpeedActuator(
        dcm, mem, "WheelFR")
    wheel_fl_speed_actuator = subdevice.WheelSpeedActuator(
        dcm, mem, "WheelFL")
    wheel_b_speed_actuator  = subdevice.WheelSpeedActuator(
        dcm, mem, "WheelB")

    # Random fractions for wheels' speeds
    fraction_wheel_fr = float(format(random.uniform(
        min_fraction, max_fraction), '.2f'))
    fraction_wheel_fl = float(format(random.uniform(
        min_fraction, max_fraction), '.2f'))
    fraction_wheel_b  = float(format(random.uniform(
        0.1, 0.2), '.2f'))

    # Set wheels' speeds [rad/s]
    speed_fr = fraction_wheel_fr * wheel_fr_speed_actuator.maximum
    speed_fl = fraction_wheel_fl * wheel_fl_speed_actuator.maximum
    speed_b  = fraction_wheel_b  * wheel_b_speed_actuator.maximum

    alea1 = int(random.uniform(0, max_random))
    alea2 = int(random.uniform(0, max_random))

    if alea1 <= 5:
        timed_commands_wheelfr = [(-speed_fr, wait_time)]
        timed_commands_wheelfl = [(speed_fl, wait_time)]
        timed_commands_wheelb  = [(speed_b, wait_time)]
    else:
        timed_commands_wheelfr = [(speed_fr, wait_time)]
        timed_commands_wheelfl = [(-speed_fl, wait_time)]
        timed_commands_wheelb  = [(speed_b, wait_time)]

    if alea2 <= 5:
        timed_commands_wheelb  = [(0.0, wait_time)]

        wheel_fr_speed_actuator.mqvalue = timed_commands_wheelfr
        wheel_fl_speed_actuator.mqvalue = timed_commands_wheelfl
        wheel_b_speed_actuator.mqvalue  = timed_commands_wheelb

        liste = [timed_commands_wheelfr,
                 timed_commands_wheelfl,
                 timed_commands_wheelb]
        return liste
    else:
        timed_commands_wheelfr = [(0.5*speed_fr, wait_time)]
        timed_commands_wheelfl = [(-0.5*speed_fl, wait_time)]

        wheel_fr_speed_actuator.mqvalue = timed_commands_wheelfr
        wheel_fl_speed_actuator.mqvalue = timed_commands_wheelfl
        wheel_b_speed_actuator.mqvalue  = timed_commands_wheelb

        liste = [timed_commands_wheelfr,
                 timed_commands_wheelfl,
                 timed_commands_wheelb]
        return liste


def test_move_random(dcm, mem, leds, wait_time, wait_time_bumpers,
                     min_fraction, max_fraction, max_random,
                     stop_robot, wake_up_pos_brakes_closed,
                     stiff_robot_wheels, unstiff_joints,
                     log_wheels_speed, log_bumper_pressions):

    '''
    The robot moves randomly
    '''

    # To modify shoulder leds
    leds.createGroup("shoulder_group", SHOULDER_LEDS)
    leds.on("shoulder_group")

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

    # Wheel temperature sensors
    wheel_fr_temperature = subdevice.WheelTemperatureSensor(
        dcm, mem, "WheelFR")
    wheel_fl_temperature = subdevice.WheelTemperatureSensor(
        dcm, mem, "WheelFL")
    wheel_b_temperature = subdevice.WheelTemperatureSensor(
        dcm, mem, "WheelB")

    # Wheel stiffness actuators
    wheel_fr_stiffness_actuator = subdevice.WheelStiffnessActuator(
        dcm, mem, "WheelFR")
    wheel_fl_stiffness_actuator = subdevice.WheelStiffnessActuator(
        dcm, mem, "WheelFL")
    wheel_b_stiffness_actuator  = subdevice.WheelStiffnessActuator(
        dcm, mem, "WheelB")

    # Bumpers
    bumper_right = subdevice.Bumper(dcm, mem, "FrontRight")
    bumper_left  = subdevice.Bumper(dcm, mem, "FrontLeft")
    bumper_back  = subdevice.Bumper(dcm, mem, "Back")

    #---------------------------------------------------------#
    #--------------- Cables crossing detection ---------------#
    #---------------------------------------------------------#
    parameters_cables = tools.read_section(
        "config.cfg", "CablesRoutingParameters")

    #---------------------------------------------------------#
    #-------------- Bumpers activation detection -------------#
    #---------------------------------------------------------#
    parameters_bumpers = tools.read_section(
        "config.cfg", "BumpersActivationsParameters")

    flag_test = tools.read_section("config.cfg", "TestChoice")

    if bool(flag_test["test_bumpers"][0]):
        bumper_detection = mobile_base_utils.BumpersCounting(dcm, mem,
        wait_time_bumpers)
        bumper_detection.start()

    if bool(flag_test["test_cables_crossing"][0]):
        cable_detection = mobile_base_utils.CablesCrossing(dcm, mem)
        cable_detection.start()

    #---------------------------------------------------------#
    #------------------ Launch the movement ------------------#
    #---------------------------------------------------------#
    while bumper_right.value == 1 or \
          bumper_left.value  == 1 or \
          bumper_back.value  == 1:
        print("One or more bumpers are blocked --> Unlock them to begin test")
        if bumper_right.value == 1:
            leds.fadeRGB("FaceLeds", "red", 0.)
        if bumper_left.value == 1:
            leds.fadeRGB("FaceLeds", "green", 0.)
        if bumper_back.value == 1:
            leds.fadeRGB("FaceLeds", "blue", 0.)
        tools.wait(dcm, wait_time)
    leds.reset("FaceLeds")

    liste_commands = move_random(dcm, mem, wait_time,

    #---------------------------------------------------------#
    #----------------------- Main Loop -----------------------#
    #---------------------------------------------------------#
    print("Main Loop\n")
    flag_bumpers = False
    flag_cables  = False

    while flag_bumpers == False or flag_cables == False:

        if bumper_detection._is_bumper_pressed == True:
            print("\nBumper pressed => robot is stopped")
            wheel_fr_speed_actuator.qvalue = (0.0, 0)
            wheel_fl_speed_actuator.qvalue = (0.0, 0)
            wheel_b_speed_actuator.qvalue  = (0.0, 0)

            timed_commands_wheelfr = [( (-1) * liste_commands[0][0][0],
                                      wait_time)]
            timed_commands_wheelfl = [( (-1) * liste_commands[1][0][0],
                                      wait_time)]
            timed_commands_wheelb  = [( (-1) * liste_commands[2][0][0],
                                      wait_time)]

            print("Going back")
            wheel_fr_speed_actuator.mqvalue = timed_commands_wheelfr
            wheel_fl_speed_actuator.mqvalue = timed_commands_wheelfl
            wheel_b_speed_actuator.mqvalue  = timed_commands_wheelb

            tools.wait(dcm, 2*wait_time)

            wheel_fr_speed_actuator.qvalue = (0.0, 0)
            wheel_fl_speed_actuator.qvalue = (0.0, 0)
            wheel_b_speed_actuator.qvalue  = (0.0, 0)

            while bumper_right.value == 1 or \
                  bumper_left.value  == 1 or \
                  bumper_back.value  == 1:
                print("Bumper blocked")
                if bumper_right.value == 1:
                    leds.fadeRGB("FaceLeds", "red", 0.)
                if bumper_left.value == 1:
                    leds.fadeRGB("FaceLeds", "green", 0.)
                if bumper_back.value == 1:
                    leds.fadeRGB("FaceLeds", "blue", 0.)
                tools.wait(dcm, wait_time)
            leds.reset("FaceLeds")

            print("Random again\n")
            liste_commands = move_random(dcm, mem, wait_time,
        else:
            try:
                pass
            except KeyboardInterrupt:
                flag_bumpers = True
                flag_cables  = True

        if bool(flag_test["test_bumpers"][0]) and \
                bumper_detection.bumpers_activations > \
                int(parameters_bumpers["nb_bumper_activations"][0]):
            flag_bumpers = True

        if bool(flag_test["test_cables_crossing"][0]) and \
                cable_detection.cables_crossing > \
                int(parameters_cables["Nb_cables_crossing"][0]):
            flag_cables = True

        # Stops briefly the test if wheels are too hot
        if wheel_fr_temperature.status == 2 or \
           wheel_fl_temperature.status == 2 or \
           wheel_b_temperature.status  == 2:

            print("Wheels too hot --> Waiting")
            leds.fadeListRGB("shoulder_group", [0x00FF00FF,], [0.,])

            wheel_fr_speed_actuator.qvalue = (0.0, 0)
            wheel_fl_speed_actuator.qvalue = (0.0, 0)
            wheel_b_speed_actuator.qvalue  = (0.0, 0)

            wheel_fr_stiffness_actuator.qvalue = (0.0, 0)
            wheel_fl_stiffness_actuator.qvalue = (0.0, 0)
            wheel_b_stiffness_actuator.qvalue  = (0.0, 0)

            # Wait for status = 1
            while wheel_fr_temperature.status != 0 or \
                  wheel_fl_temperature.status != 0 or \
                  wheel_b_temperature.status  != 0:
                print("Wheels too hot --> Waiting")
                tools.wait(dcm, 30000)

            print("Random again\n")
            leds.reset("shoulder_group")
            wheel_fr_stiffness_actuator.qvalue = (1.0, 0)
            wheel_fl_stiffness_actuator.qvalue = (1.0, 0)
            wheel_b_stiffness_actuator.qvalue  = (1.0, 0)
            liste_commands = move_random(dcm, mem, wait_time,
                                         min_fraction, max_fraction, max_random)
