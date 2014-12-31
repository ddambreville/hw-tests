#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on 2014/12/31

@author: Emmanuel NALEPA
@contact: enalepa[at]aldebaran-robotics.com
@copyright: Aldebaran Robotics 2014
@requires:  - naoqi python SDK  (Available on Version Gate)
@platform : - Windows, Linux (PC or robot), OS X
@summary: This module permits to retrieve ALMemory value from several robots
@pep8 : Complains without all rules
"""

from naoqi import ALProxy
import argparse

DEFAULT_LIST_IP = "list_IP.cfg"


def main():
    """Read the configuration file and retrieve values."""
    parser = argparse.ArgumentParser( description="Retrieve 1 ALMemory,\
    usage, description, epilog, version, parents value from several robots")

    parser.add_argument("-i", "--IP", dest="list_ip",
                        default=DEFAULT_LIST_IP,
                        help="configuration file containing the list of IP\
                      adress (default: multi_logger.cfg)")

    parser.add_argument(dest="key", help="ALMemory key")

    args = parser.parse_args()

    # Open file containing all IP address
    list_ip_file = open(args.list_ip, "r")

    # Create a string with all IP address
    list_ip_string = list_ip_file.read()

    # Create a list with all IP address
    list_ip = list_ip_string.split("\n")

    # Remove empty lines
    while "" in list_ip:
        list_ip.remove("")

    # Create dic_dcm_robot
    dic_mem_robot = {}

    # Connect to the ALMemory to all robots in the list
    for ip_address in list_ip:
        try:
            mem = ALProxy("ALMemory", ip_address, 9559)

            try:
                value = mem.getData(args.key)
            except RuntimeError:
                value = "Key not found"

        except RuntimeError:
            value = "Robot not found"

        dic_mem_robot[ip_address] = value

    # Print results on screen
    print
    print "IP -", args.key
    for key, value in dic_mem_robot.items():
        try:
            value = round(value)
        except TypeError:
            pass

        print key, "-", value

    print

if __name__ == '__main__':
    main()
