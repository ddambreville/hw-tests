import pytest
import tools
import subdevice
import threading
import math
import random
import mobile_base_utils


def is_bumper_pressed(dcm, mem, test_time, wait_time_bumpers):
    """
    Returns True if one or more bumpers are pressed
    """

    bumper_right = subdevice.Bumper(dcm, mem, "FrontRight")
    bumper_left  = subdevice.Bumper(dcm, mem, "FrontLeft")
    bumper_back  = subdevice.Bumper(dcm, mem, "Back")

    list_bumpers = [bumper_right, bumper_left, bumper_back]

    timer = tools.Timer(dcm, test_time)

    while timer.is_time_not_out():
        flag = 0
        for bumper in list_bumpers:
            if bumper.value == 1:
                flag += 1
        if flag > 0:
            return True
        tools.wait(dcm, wait_time_bumpers)


def move_random(dcm, mem, wait_time, min_speed, max_speed):
    """
    Makes the robot move randomly
    """
    wheelfr_speed_actuator = subdevice.WheelSpeedActuator(dcm, mem, "WheelFR")
    wheelfl_speed_actuator = subdevice.WheelSpeedActuator(dcm, mem, "WheelFL")
    wheelb_speed_actuator  = subdevice.WheelSpeedActuator(dcm, mem, "WheelB")

    # random fractions for wheels' speeds
    fraction_wheel_fr = float(format(random.uniform(min_speed, max_speed), '.2f'))
    fraction_wheel_fl = float(format(random.uniform(min_speed, max_speed), '.2f'))
    fraction_wheel_b  = float(format(random.uniform(min_speed, max_speed), '.2f'))

    # set vwheels' speeds [rad/s]
    speed_fr = fraction_wheel_fr * wheelfr_speed_actuator.maximum
    speed_fl = fraction_wheel_fl * wheelfl_speed_actuator.maximum
    speed_b  = fraction_wheel_b  * wheelb_speed_actuator.maximum

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

        wheelfr_speed_actuator.mqvalue = timed_commands_wheelfr
        wheelfl_speed_actuator.mqvalue = timed_commands_wheelfl
        wheelb_speed_actuator.mqvalue  = timed_commands_wheelb

        liste = [timed_commands_wheelfr, timed_commands_wheelfl, timed_commands_wheelb]
        return liste
    else:
        timed_commands_wheelfr = [(0.5*speed_fr, wait_time)]
        timed_commands_wheelfl = [(-0.5*speed_fl, wait_time)]

        wheelfr_speed_actuator.mqvalue = timed_commands_wheelfr
        wheelfl_speed_actuator.mqvalue = timed_commands_wheelfl
        wheelb_speed_actuator.mqvalue  = timed_commands_wheelb

        liste = [timed_commands_wheelfr, timed_commands_wheelfl, timed_commands_wheelb]
        return liste


def test_move_random(dcm, mem, wait_time, test_time, max_random, stop_robot,
                     wake_up_pos_brakes_closed, stiff_robot_wheels,
                     unstiff_joints, log_wheels_speed,
                     log_bumper_pressions, cables_routing):
    '''
    The robot moves randomly
    '''
    # Objects creation
    wheelfr_speed_actuator = subdevice.WheelSpeedActuator(dcm, mem, "WheelFR")
    wheelfl_speed_actuator = subdevice.WheelSpeedActuator(dcm, mem, "WheelFL")
    wheelb_speed_actuator  = subdevice.WheelSpeedActuator(dcm, mem, "WheelB")

    bumper_right = subdevice.Bumper(dcm, mem, "FrontRight")
    bumper_left  = subdevice.Bumper(dcm, mem, "FrontLeft")
    bumper_back  = subdevice.Bumper(dcm, mem, "Back")

    # Cables crossing detection
    parameters = tools.read_section(
        "config_pod.cfg", "CablesRoutingParameters")
    cable_detection = mobile_base_utils.CablesCrossing(dcm, mem)
    cable_detection.start()

    flag_stop = False
    timer = tools.Timer(dcm, test_time)

    # Launch the movement
    liste_commands = move_random(dcm, mem)

    # Loop
    while timer.is_time_not_out() and flag_stop == False and\
            cable_detection.cables_crossing < \
            parameters["Nb_cables_crossing"][0]:
        if is_bumper_pressed(dcm, mem, test_time) == True:
            print("A Bumper has been pressed")
            wheelfr_speed_actuator.qvalue = (0.0, 0)
            wheelfl_speed_actuator.qvalue = (0.0, 0)
            wheelb_speed_actuator.qvalue = (0.0, 0)
            tools.wait(dcm, wait_time)

            print("Robot going back")
            timed_commands_wheelfr = [( (-1) * liste_commands[0][0][0], wait_time)]
            timed_commands_wheelfl = [( (-1) * liste_commands[1][0][0], wait_time)]
            timed_commands_wheelb  = [( (-1) * liste_commands[2][0][0], wait_time)]
            wheelfr_speed_actuator.mqvalue = timed_commands_wheelfr
            wheelfl_speed_actuator.mqvalue = timed_commands_wheelfl
            wheelb_speed_actuator.mqvalue  = timed_commands_wheelb
            tools.wait(dcm, wait_time)

            while bumper_right.value == 1 or \
                  bumper_left.value  == 1 or \
                  bumper_back.value == 1:
                print "A bumper is blocked"

            print("Start random again\n")
            liste_commands = move_random(dcm, mem)
        else:
            try:
                pass
            except KeyboardInterrupt:
                print("Key board interrupt")
                flag_stop = True
