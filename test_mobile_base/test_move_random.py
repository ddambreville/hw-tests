import pytest
import tools
import subdevice
import threading
import math
import random

def is_bumper_pressed(dcm, mem, test_time):
    """
    If one or more bumpers are pressed,
    it returns True and saves wheels' speeds (rad/s)
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
        tools.wait(dcm, 100)


def move_random(dcm, mem):
    """ 
    Makes the robot move randomly
    """
    wheelfr_speed_actuator = subdevice.WheelSpeedActuator(dcm, mem, "WheelFR")
    wheelfl_speed_actuator = subdevice.WheelSpeedActuator(dcm, mem, "WheelFL")
    wheelb_speed_actuator  = subdevice.WheelSpeedActuator(dcm, mem, "WheelB")

    # random fractions for wheels' speeds
    fraction_wheelFR = float(format(random.uniform(0.1, 0.15), '.2f'))
    fraction_wheelFL = float(format(random.uniform(0.1, 0.15), '.2f'))
    fraction_wheelB  = float(format(random.uniform(0.1, 0.15), '.2f'))

    # set vwheels' speeds [rad/s]
    speed_FR = fraction_wheelFR * wheelfr_speed_actuator.maximum
    speed_FL = fraction_wheelFL * wheelfl_speed_actuator.maximum
    speed_B  = fraction_wheelB  * wheelb_speed_actuator.maximum

    t = 2000
    alea1 = int(random.uniform(0,10))
    alea2 = int(random.uniform(0,10))

    if alea1 <= 5:
        timed_commands_wheelfr = [(-speed_FR, t)]
        timed_commands_wheelfl = [(speed_FL, t)]
        timed_commands_wheelb  = [(speed_B, t)]
    else:
        timed_commands_wheelfr = [(speed_FR, t)]
        timed_commands_wheelfl = [(-speed_FL, t)]
        timed_commands_wheelb  = [(speed_B, t)]

    if alea2 <= 5:
        timed_commands_wheelb  = [(0.0, t)]

        wheelfr_speed_actuator.mqvalue = timed_commands_wheelfr
        wheelfl_speed_actuator.mqvalue = timed_commands_wheelfl
        wheelb_speed_actuator.mqvalue  = timed_commands_wheelb

        liste = [timed_commands_wheelfr, timed_commands_wheelfl, timed_commands_wheelb]
        return liste
    else:
        timed_commands_wheelfr = [(0.5*speed_FR, t)]
        timed_commands_wheelfl = [(-0.5*speed_FL, t)]

        wheelfr_speed_actuator.mqvalue = timed_commands_wheelfr
        wheelfl_speed_actuator.mqvalue = timed_commands_wheelfl
        wheelb_speed_actuator.mqvalue  = timed_commands_wheelb

        liste = [timed_commands_wheelfr, timed_commands_wheelfl, timed_commands_wheelb]
        return liste


def test_move_random(dcm, mem, rest_pos, wake_up_pos, kill_motion, 
                     stiff_robot, stiff_robot_wheels, test_time, 
                     stop_robot, wakeUp, unstiff_joints, log_wheels_speed, 
                     log_bumper_pressions):
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

    flag_stop = False
    timer = tools.Timer(dcm, test_time)

    # Launch the movement
    liste_commands = move_random(dcm, mem)

    # Loop
    while timer.is_time_not_out() and flag_stop == False:
        if is_bumper_pressed(dcm, mem, test_time) == True:
            print("Bumper pressed - robot stopped")
            wheelfr_speed_actuator.qvalue = (0.0, 0)
            wheelfr_speed_actuator.qvalue = (0.0, 0)
            wheelfr_speed_actuator.qvalue = (0.0, 0)
            tools.wait(dcm, 2000)

            print("Robot going back")
            t = 2000
            timed_commands_wheelfr = [( (-1) * liste_commands[0][0][0], t)]
            timed_commands_wheelfl = [( (-1) * liste_commands[1][0][0], t)]
            timed_commands_wheelb  = [( (-1) * liste_commands[2][0][0], t)]
            wheelfr_speed_actuator.mqvalue = timed_commands_wheelfr
            wheelfl_speed_actuator.mqvalue = timed_commands_wheelfl
            wheelb_speed_actuator.mqvalue  = timed_commands_wheelb
            tools.wait(dcm, 2000)

            while bumper_right.value == 1 or \
                  bumper_left.value  == 1 or \
                  bumper_back.value == 1:
                print "bumper is blocked"

            print("Start random again\n")
            liste_commands = move_random(dcm, mem)
        else:
            try:
                pass
            except KeyboardInterrupt:
                print("Key board interrupt")
                flag_stop = True

    print("Robot goes to rest")


