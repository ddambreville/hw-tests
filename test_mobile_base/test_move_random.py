import pytest
import tools
import subdevice
import threading
import math
import random
import mobile_base_utils


def is_bumper_pressed(dcm, mem, wait_time_bumpers):
    """Returns True if one or more bumpers are pressed"""
    bumper_right = subdevice.Bumper(dcm, mem, "FrontRight")
    bumper_left  = subdevice.Bumper(dcm, mem, "FrontLeft")
    bumper_back  = subdevice.Bumper(dcm, mem, "Back")

    list_bumpers = [bumper_right, bumper_left, bumper_back]

    timer = tools.Timer(dcm, 1000000000)

    while timer.is_time_not_out():
        flag = 0
        for bumper in list_bumpers:
            if bumper.value == 1:
                flag += 1
        if flag > 0:
            return True
        tools.wait(dcm, wait_time_bumpers)


def move_random(dcm, mem, wait_time, min_fraction, max_fraction, max_random):
    """
    Makes the robot move randomly
    """
    wheel_fr_speed_actuator = subdevice.WheelSpeedActuator(
        dcm, mem, "WheelFR")
    wheel_fl_speed_actuator = subdevice.WheelSpeedActuator(
        dcm, mem, "WheelFL")
    wheel_b_speed_actuator  = subdevice.WheelSpeedActuator(
        dcm, mem, "WheelB")

    # random fractions for wheels' speeds
    fraction_wheel_fr = float(format(random.uniform(
        min_fraction, max_fraction), '.2f'))
    fraction_wheel_fl = float(format(random.uniform(
        min_fraction, max_fraction), '.2f'))
    fraction_wheel_b  = float(format(random.uniform(
        0.1, 0.2), '.2f'))

    # set vwheels' speeds [rad/s]
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


def test_move_random(dcm, mem, wait_time, wait_time_bumpers,
                     min_fraction, max_fraction, max_random,
                     stop_robot, wake_up_pos_brakes_closed,
                     stiff_robot_wheels, unstiff_joints,
                     log_wheels_speed, log_bumper_pressions,
                     nb_cables_crossing):
    '''
    The robot moves randomly
    '''
    #---------------------------------------------------------#
    #-------------------- Object creations -------------------#
    #---------------------------------------------------------#

    # WHEELS
    wheel_fr_speed_actuator = subdevice.WheelSpeedActuator(
        dcm, mem, "WheelFR")
    wheel_fl_speed_actuator = subdevice.WheelSpeedActuator(
        dcm, mem, "WheelFL")
    wheel_b_speed_actuator  = subdevice.WheelSpeedActuator(
        dcm, mem, "WheelB")

    # BUMPERS
    bumper_right = subdevice.Bumper(dcm, mem, "FrontRight")
    bumper_left  = subdevice.Bumper(dcm, mem, "FrontLeft")
    bumper_back  = subdevice.Bumper(dcm, mem, "Back")

    #---------------------------------------------------------#
    #--------------- Cables crossing detection ---------------#
    #---------------------------------------------------------#
    parameters_cables = tools.read_section(
        "config.cfg", "CablesRoutingParameters")
    cable_detection = mobile_base_utils.CablesCrossing(dcm, mem)
    cable_detection.start()

    #---------------------------------------------------------#
    #-------------- Bumpers activation detection -------------#
    #---------------------------------------------------------#
    parameters_bumpers = tools.read_section(
        "config.cfg", "BumpersActivationsParameters")
    bumper_detection = mobile_base_utils.BumpersCounting(dcm, mem,
        wait_time_bumpers)
    bumper_detection.start()

    # TESTS RAPIDES POUR VERIFIER QUE CA MARCHE
    # while cable_detection.cables_crossing < nb_cables_crossing:
    #     pass
    # while bumper_detection.bumpers_activations < \
    #       int(parameters_bumpers["nb_bumper_activations"][0]):
    #     pass

    #---------------------------------------------------------#
    #------------------ Launch the movement ------------------#
    #---------------------------------------------------------#
    liste_commands = move_random(dcm, mem, wait_time,
                                 min_fraction, max_fraction, max_random)

    #---------------------------------------------------------#
    #----------------------- Main Loop -----------------------#
    #---------------------------------------------------------#
    flag_stop = False
    while flag_stop == False and \
          cable_detection.cables_crossing < nb_cables_crossing and\
          bumper_detection.bumpers_activations < \
          int(parameters_bumpers["nb_bumper_activations"][0]):

        if is_bumper_pressed(dcm, mem, wait_time_bumpers) == True:
            # print("\nBumper pressed => We stop the robot\n")
            wheel_fr_speed_actuator.qvalue = (0.0, 0)
            wheel_fl_speed_actuator.qvalue = (0.0, 0)
            wheel_b_speed_actuator.qvalue  = (0.0, 0)
            # tools.wait(dcm, wait_time)

            # print("\nRobot going back\n")
            timed_commands_wheelfr = [( (-1) * liste_commands[0][0][0],
                                      wait_time)]
            timed_commands_wheelfl = [( (-1) * liste_commands[1][0][0],
                                      wait_time)]
            timed_commands_wheelb  = [( (-1) * liste_commands[2][0][0],
                                      wait_time)]

            wheel_fr_speed_actuator.mqvalue = timed_commands_wheelfr
            wheel_fl_speed_actuator.mqvalue = timed_commands_wheelfl
            wheel_b_speed_actuator.mqvalue  = timed_commands_wheelb
            tools.wait(dcm, wait_time)

            while bumper_right.value == 1 or \
                  bumper_left.value  == 1 or \
                  bumper_back.value  == 1:
                pass
                # print("\nBumper blocked !\n")

            # print("\nRandom again\n")
            liste_commands = move_random(dcm, mem, wait_time,
                                         min_fraction, max_fraction, max_random)
        else:
            try:
                pass
            except KeyboardInterrupt:
                print("Key board interrupt")
                flag_stop = True
