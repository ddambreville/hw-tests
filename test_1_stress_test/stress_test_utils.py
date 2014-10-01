import pytest
import subdevice
from math import pi
import time


def motion_explore(motion, param_dico, offset_protection):
    """
    Joint exploration from configuration file section.
    An offset is settable to not damage mechanical stop on a new robot
    (if command is 'min' or 'max').
    """
    # defining cycle number
    if param_dico.has_key("NbCycles"):
        nb_cycles = int(param_dico["NbCycles"][0])
        del param_dico["NbCycles"]
    else:
        nb_cycles = 1

    # Lists initialization
    joint_list = param_dico.keys()
    angle_list = list()
    time_list = list()

    # checking parameters number
    parameters_number = len(param_dico.values()[0])
    timed_command_number = parameters_number / 2

    # fill time_list
    for joint in joint_list:
        joint_times = list()
        for i in range(0, timed_command_number):
            joint_times.append(float(param_dico[joint][i]))
        time_list.append(joint_times)

    # fill angle_list
    for joint, excursion_parameter in param_dico.items():

        min_angle = float(motion.getLimits(joint)[0][0])
        max_angle = float(motion.getLimits(joint)[0][1])
        if min_angle < 0.0:
            min_angle = min_angle - offset_protection
        else:
            min_angle = min_angle + offset_protection
        if max_angle > 0.0:
            max_angle = max_angle + offset_protection
        else:
            max_angle = max_angle - offset_protection

        joint_angles = list()
        for i in range(timed_command_number, parameters_number):
            if excursion_parameter[i] == 'max':
                excursion_parameter[i] = max_angle
            elif excursion_parameter[i] == 'min':
                excursion_parameter[i] = min_angle
            joint_angles.append(excursion_parameter[i])
        angle_list.append(joint_angles)

    # creating the desired motion
    # True parameter is to allow absolute angles (else it would be relative)
    for x in range(nb_cycles):
        motion.angleInterpolation(joint_list, angle_list, time_list, True)


def no_obstacle_detected(dcm, mem, distance):
    """
    Return True if no obstacle is tetected by the sonars.
    """
    front_sonar = subdevice.Sonar(dcm, mem, "Front")
    back_sonar = subdevice.Sonar(dcm, mem, "Back")
    if front_sonar.value > distance and back_sonar.value > distance:
        return True
    else:
        return False


def rotate(motion):
    """
    @param motion : Proxy to ALMotion naoqi module
    @type  motion : object

    @returns : Nothing. The robot makes one turn on itself.
    """
    motion.moveTo(0.0, 0.0, 2 * pi)


def check_battery_level(battery_charge, limit_level):
    """
    @param battery_charge : object created from subdevice.py
    @type  battery_charge : object
    @param limit_level : battery charge limit tolerated. Must be between [0,1]
    @type  limit_level : float

    @returns : True if battery level is higher than limit_level.
    @rtype : Boolean
    """
    print "checking that battery level is higher than " + str(limit_level)
    current_battery_level = battery_charge.value
    print "current battery level " + str(current_battery_level)
    if current_battery_level >= limit_level:
        return True
    else:
        return False


def cycle_brakes(motion):
    """Cycle robot brakes."""
    print "cycling brakes..."
    minimum_leg_stiffness = 0.6
    # Change minimum stiffness parameter to make Motion
    # think that the robot is still woken up when no stiffness on leg
    motion.setMotionConfig(
        [['SMART_STIFFNESS_MINIMUM_LEG_STIFFNESS', 0.00001]])
    # set stiffness low enough for brake activation
    motion._setStiffnesses('KneePitch', 0.0001)
    motion._setStiffnesses('HipPitch', 0.0001)
    time.sleep(4.0)
    # Do not reset stiffness on both joints at the same time to
    # avoid current peaks
    motion._setStiffnesses('KneePitch', 1.0)
    time.sleep(0.1)
    motion._setStiffnesses('HipPitch', 1.0)
    time.sleep(0.1)
    # reset minimum stiffness parameter to default value
    motion.setMotionConfig(
        [['SMART_STIFFNESS_MINIMUM_LEG_STIFFNESS', minimum_leg_stiffness]])


def check_nacks(dcm, mem, boards, accepted_ratio):
    """
    Find all the joints boards and check if it does not nack.
    """
    print "checking nacks..."
    flag = True
    for board in boards:
        board_obj = subdevice.Device(dcm, mem, board)
        acks = board_obj.ack
        nacks = board_obj.nack
        ratio = float(nacks) / float(acks)
        if ratio >= float(accepted_ratio):
            flag = False
            print "ratio = " + str(ratio) + "for " + str(board)
            break
    return flag


def no_overheat(body_initial_temperatures, get_joints_temperature,
                allowed_temperature_emergencies):
    """
    Return False if one of the joints is too hot conpared to allowed
    temperature emergencies availables in configuration file.
    Return True if no overheat.
    """
    flag = True
    for joint in body_initial_temperatures.keys():
        joint_ini_tmp = body_initial_temperatures[joint]
        allowed_tmp_emergency = float(
            allowed_temperature_emergencies[joint][0])
        joint_tmp = get_joints_temperature[joint]
        if joint_tmp >= joint_ini_tmp + allowed_tmp_emergency:
            flag = False
            break
    return flag


def get_joints_temperature(joint_temperature_object):
    """Returns a dictionnary containing each joint temperature."""
    dico_temperature = dict()
    for joint, joint_tmp_object in joint_temperature_object.items():
        dico_temperature[joint] = float(joint_tmp_object.value)
    return dico_temperature


def go_to_stand_pos(robot_posture_proxy, speed_fraction):
    """
    Robot goes to standInit posture at speed fraction percent of max speed.
    """
    print "going to stand init posture..."
    robot_posture_proxy.goToPosture("StandInit", speed_fraction)
