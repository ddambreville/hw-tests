#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    This file describes the test of brake slip repeatability
"""

import argparse
import subdevice
import qha_tools
import time
import os
from naoqi import ALProxy


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Log datas from ALMemory")

    parser.add_argument(dest="robot_ip",
                        help="Robot IP or name")

    args = parser.parse_args()

    general = qha_tools.read_section("slip.cfg", "general")

    robot_ip = args.robot_ip
    result_folder = general["resultsFolder"][0]

    # Create result folder if not existing
    try:
        os.mkdir(result_folder)
    except OSError:
        pass

    dcm = ALProxy("DCM", robot_ip, 9559)
    mem = ALProxy("ALMemory", robot_ip, 9559)

    # Get Body ID
    body_id = mem.getData("Device/DeviceList/ChestBoard/BodyId")

    # Kill motion (if not already done)
    try:
        mot = ALProxy("ALMotion", robot_ip, 9559)
        mot.exit()
    except RuntimeError:
        pass

    print "[I] ALMotion is now killed"

    # Ask the operator to write his name
    name = raw_input("Please enter your name and press Enter : ")

    while name == "":
        name = raw_input("Please enter your name and press Enter : ")

    nb_of_trials = int(general["numberOfTrials"][0])

    stiffness_on = qha_tools.read_section("slip.cfg",
                                          "stiffnessOnWithoutWheels")

    stiffness_off = qha_tools.read_section("slip.cfg",
                                           "stiffnessOff")

    rest_pos = qha_tools.read_section("slip.cfg", "restPosition")

    force_list = []

    for i in range(nb_of_trials):
        # Set Stiffness on
        subdevice.multiple_set(dcm, mem, stiffness_on)

        # Go to rest position
        subdevice.multiple_set(dcm, mem, rest_pos, wait=True)
        time.sleep(1)

        # Set Stiffness off
        subdevice.multiple_set(dcm, mem, stiffness_off)

        if (nb_of_trials - i - 1) <= 1:
            trial_string = "trial"
        else:
            trial_string = "trials"

        force = raw_input("Please push the robot, write the force (in Newton) "
                          "and press Enter. (" + str(nb_of_trials - i - 1) +
                          " " + trial_string + " left) : ")

        while not is_number(force):
            force = raw_input("Please push the robot, write the force"
                              "(in Newton) and press Enter. (" +
                              str(nb_of_trials - i - 1) + " " + trial_string
                              + " left) : ")

        force_list.append(force)

    print ("Thank you !")

    # At the end of the test, put the robot in initial position
    # Set Stiffness on
    subdevice.multiple_set(dcm, mem, stiffness_on)

    # Go to rest position
    subdevice.multiple_set(dcm, mem, rest_pos, wait=True)
    time.sleep(1)

    # Set Stiffness off
    subdevice.multiple_set(dcm, mem, stiffness_off)

    # Write results file
    file_path = result_folder + "/" + body_id + ".dat"
    my_file = open(file_path, 'a')

    string_to_print = name + " " + " ".join(force_list) + "\n"

    my_file.write(string_to_print)


def is_number(my_string):
    """Check if a string is a number or not"""
    try:
        float(my_string)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(my_string)
        return True
    except (TypeError, ValueError):
        pass

    return False

# Call the main function
if __name__ == '__main__':
    main()
