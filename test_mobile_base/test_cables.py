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
    for speed in list_wheel_speed:
        speed.qvalue = (0.0, 0)


def check_wheel_temperatures(dcm, leds, list_wheel_temperature,
                             list_wheel_speed, list_wheel_stiffness):
    """
    Pauses the robot if the wheels are too hot
    """

    parameters_cables = tools.read_section("config.cfg",
                                           "CablesRoutingParameters")
    Temp_max = int(parameters_cables["Temp_max"][0])
    Temp_min = int(parameters_cables["Temp_min"][0])

    if list_wheel_temperature[0].value >= Temp_max or \
       list_wheel_temperature[1].value >= Temp_max or \
       list_wheel_temperature[2].value >= Temp_max:

        print("\nWheels too hot --> Waiting")
        leds.fadeListRGB("shoulder_group", [0x00FF00FF, ], [0., ])
        stop_robot(list_wheel_speed)
        unstiff_wheels(list_wheel_stiffness)

        # Wait
        while list_wheel_temperature[0].value >= Temp_min or \
                list_wheel_temperature[1].value >= Temp_min or \
                list_wheel_temperature[2].value >= Temp_min:
            tools.wait(dcm, 20000)

        leds.reset("shoulder_group")
        stiff_wheels(list_wheel_stiffness)


def move_robot(dcm, mem, wait_time, list_wheels_to_use):
    """
    Makes the robot move.
    - The robot uses for each sequence two wheels and lets
    the third one unstiffed.
    - The speed is the same for the 3 wheels.
    - It returns the wheels used for each sequence.
    """

    #---------------------------------------------------------#
    #-------------------- Object creations -------------------#
    #---------------------------------------------------------#

    # Wheel speed actuators
    wheel_fr_speed_actuator = subdevice.WheelSpeedActuator(
        dcm, mem, "WheelFR")
    wheel_fl_speed_actuator = subdevice.WheelSpeedActuator(
        dcm, mem, "WheelFL")
    wheel_b_speed_actuator = subdevice.WheelSpeedActuator(
        dcm, mem, "WheelB")

    # Same speed for the 3 wheels
    speed_fraction = 0.3
    speed = speed_fraction * wheel_fr_speed_actuator.maximum

    # To know which wheels are used for each sequence
    list_stiffed_wheels = []

    # Make the robot move according to the wheels to use
    #-------------------------- CASE 1 -------------------------#
    if list_wheels_to_use[0] == 1 and list_wheels_to_use[1] == 1:

        wheel_fr_speed_actuator.mqvalue = [(-speed, wait_time)]
        wheel_fl_speed_actuator.mqvalue = [(speed, wait_time)]

        list_stiffed_wheels.append('fr')
        list_stiffed_wheels.append('fl')

        return list_stiffed_wheels

    #-------------------------- CASE 2 -------------------------#
    if list_wheels_to_use[1] == 1 and list_wheels_to_use[2] == 1:

        wheel_fl_speed_actuator.mqvalue = [(-speed, wait_time)]
        wheel_b_speed_actuator.mqvalue = [(speed, wait_time)]

        list_stiffed_wheels.append('fl')
        list_stiffed_wheels.append('b')

        return list_stiffed_wheels

    #-------------------------- CASE 3 -------------------------#
    if list_wheels_to_use[2] == 1 and list_wheels_to_use[0] == 1:

        wheel_b_speed_actuator.mqvalue = [(-speed, wait_time)]
        wheel_fr_speed_actuator.mqvalue = [(speed, wait_time)]

        list_stiffed_wheels.append('b')
        list_stiffed_wheels.append('fr')

        return list_stiffed_wheels


def test_move_random(motion, dcm, mem, leds, expressiveness, wait_time,
                     wait_time_bumpers, min_fraction, max_fraction, max_random,
                     stop_robot, wakeup_no_rotation,
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
    motion.setExternalCollisionProtectionEnabled('All', False)

    # Switch off eyes and ears leds
    leds.off('FaceLeds')
    leds.off('EarLeds')

    # Switch on shoulder leds
    leds.createGroup("shoulder_group", SHOULDER_LEDS)
    leds.on("shoulder_group")

    #----------------------------------------------------------#
    #--------------------- Test selection ---------------------#
    #----------------------------------------------------------#

    # Cables crossing detection
    parameters_cables = tools.read_section(
        "config.cfg", "CablesRoutingParameters")

    # Bumpers activation detection
    parameters_bumpers = tools.read_section(
        "config.cfg", "BumpersActivationsParameters")

    # Get the desired type of test
    flag_test = tools.read_section("config.cfg", "TestChoice")

    # Launch bumper counter (thread)
    if int(flag_test["test_bumpers"][0]) == 1:
        bumper_detection = mobile_base_utils.BumpersCounting(dcm, mem, leds,
                                                             wait_time_bumpers)
        bumper_detection.start()

    # Launch cable counter (thread)
    if int(flag_test["test_cables_crossing"][0]) == 1:
        cable_detection = mobile_base_utils.CablesCrossing(dcm, mem)
        cable_detection.start()

    #---------------------------------------------------------#
    #--------------------- Initialization --------------------#
    #---------------------------------------------------------#
    flag_bumpers = False
    flag_cables = False
    list_wheels_to_use = [1, 1, 0]
    #tools.wait(dcm, 30000)
    used_wheels = move_robot(dcm, mem, wait_time, list_wheels_to_use)
    tools.wait(dcm, 2000)

    acc_z = subdevice.InertialSensorBase(dcm, mem, "AccelerometerZ")

    #---------------------------------------------------------#
    #----------------------- Main Loop -----------------------#
    #---------------------------------------------------------#
    while flag_bumpers == False and flag_cables == False:

        try:
            #-------------------- Wall event -------------------#
            if (math.fabs(list_wheel_speed_sensor[0].value) < 0.10) and \
               (math.fabs(list_wheel_speed_sensor[1].value) < 0.10) and \
               (math.fabs(list_wheel_speed_sensor[2].value) < 0.10):

                # Robot hit wall --> Stop it
                list_wheel_speed_actuator[0].qvalue = (0.0, 0)
                list_wheel_speed_actuator[1].qvalue = (0.0, 0)
                list_wheel_speed_actuator[2].qvalue = (0.0, 0)

                # stop_robot(list_wheel_speed_actuator)

                # check temperatures
                check_wheel_temperatures(
                    dcm, leds, list_wheel_temperature,
                    list_wheel_speed_actuator, list_wheel_stiffness_actuator)

                alea = int(random.uniform(0, 10))

                if used_wheels[0] == 'fr' and used_wheels[1] == 'fl':

                    wheel_stiffed_1 = list_wheel_stiffness_actuator[0]
                    wheel_stiffed_2 = list_wheel_stiffness_actuator[1]

                    list_wheel_stiffness_actuator[2].qvalue = (1.0, 0)

                    if alea <= 5:
                        wheel_stiffed_1.qvalue = (0.0, 0)
                        list_wheels_to_use = [0, 1, 1]
                    else:
                        wheel_stiffed_2.qvalue = (0.0, 0)
                        list_wheels_to_use = [1, 0, 1]

                if used_wheels[0] == 'fl' and used_wheels[1] == 'b':

                    wheel_stiffed_1 = list_wheel_stiffness_actuator[1]
                    wheel_stiffed_2 = list_wheel_stiffness_actuator[2]

                    list_wheel_stiffness_actuator[0].qvalue = (1.0, 0)

                    if alea <= 5:
                        wheel_stiffed_1.qvalue = (0.0, 0)
                        list_wheels_to_use = [1, 0, 1]
                    else:
                        wheel_stiffed_2.qvalue = (0.0, 0)
                        list_wheels_to_use = [1, 1, 0]

                if used_wheels[0] == 'b' and used_wheels[1] == 'fr':

                    wheel_stiffed_1 = list_wheel_stiffness_actuator[2]
                    wheel_stiffed_2 = list_wheel_stiffness_actuator[0]

                    list_wheel_stiffness_actuator[1].qvalue = (1.0, 0)

                    if alea <= 5:
                        wheel_stiffed_1.qvalue = (0.0, 0)
                        list_wheels_to_use = [1, 1, 0]
                    else:
                        wheel_stiffed_2.qvalue = (0.0, 0)
                        list_wheels_to_use = [0, 1, 1]

                used_wheels = move_robot(
                    dcm, mem, wait_time, list_wheels_to_use)

                tools.wait(dcm, 2000)

            #-------------------- Check test variables -------------------#
            if int(flag_test["test_bumpers"][0]) == 1 and \
                    bumper_detection.bumpers_activations == \
                    int(parameters_bumpers["nb_bumper_activations"][0]):
                bumper_detection.stop()
                flag_bumpers = True

            if int(flag_test["test_cables_crossing"][0]) == 1 and \
                    cable_detection.cables_crossing == \
                    int(parameters_cables["Nb_cables_crossing"][0]):
                cable_detection.stop()
                flag_cables = True
            #-------- Robot has fallen ----------#
            if (math.fabs(acc_z.value)) < 2.0:

                if int(flag_test["test_bumpers"][0]) == 1:
                    bumper_detection.stop()

                if int(flag_test["test_cables_crossing"][0]) == 1:
                    cable_detection.stop()

                break

        # Exit test if user interrupt
        except KeyboardInterrupt:
            print "\n******* User interrupt - ending test *******"
            if int(flag_test["test_bumpers"][0]) == 1:
                bumper_detection.stop()
            if int(flag_test["test_cables_crossing"][0]) == 1:
                cable_detection.stop()
            break
