# -*- encoding: UTF-8 -*- 
'''
@author: Safran Engineering Services - Thomas CHARLES

@contact: tcharles@presta.aldebaran-robotics.fr

Name: hwdcmlib.py (Hardware DCM lib)

Creation date: 2013, November, 15th

Description: This library is made for Hardware Qualification Team in order to be able to send DCM commands easily.
             In order to avoid any conflict between ALMotion and the DCM, ALMotion must be killed before using this library.
             How to kill ALMotion library?
                 First way: Comment ALMotion in the autoload.ini file and reboot the robot
                 Second way: exit method (qicli call ALMotion.exit or Proxy to motion motionProxy.exit())
            All the methods take in argument "dcm" which is the Proxy to the robot's DCM.
                First case: Using python: Create a proxy into your main file.
                Second case: Unsing pytest: DCM is in your conftest.py 
                 
Called methods: readListFile from Hardware tools (hwtools.py)

Use example: 

    First case:
        import hwdcmlib
        hwdcmlib.DCMwakeUp(dcm)
        hwdcmlib.DCMrotate(dcm, 1)
        hwdcmlib.DCMwakeUp(dcm)

    Second case:
        from hwdcmlib import *
        DCMwakeUp(dcm)
        DCMrotate(dcm, 1)
        DCMwakeUp(dcm)
'''

import time
import math
import os

def readListFile (filepath):
    my_list = []
    for line in open(filepath, "U"):
        line = line.rstrip('\n')
        if line[0] != '#':
            my_list.append(line)
    return my_list

# ------------------------------ LIST CREATION ------------------------------

lib_path =  os.path.dirname(__file__)

wake_up_pos_path = os.path.join(lib_path, os.path.join("Configuration","WakeUpPositionList.cfg"))
norm_wake_up_path = os.path.normpath(wake_up_pos_path)

rest_pos_path = os.path.join(lib_path, os.path.join("Configuration","RestPositionList.cfg"))
norm_rest_path = os.path.normpath(rest_pos_path)

body_names_path = os.path.join(lib_path, os.path.join("Configuration","BodyNamesList.cfg"))
norm_body_names_path = os.path.normpath(body_names_path)

wheels_names_path = os.path.join(lib_path, os.path.join("Configuration","WheelsNamesList.cfg"))
norm_wheels_names_path = os.path.normpath(wheels_names_path)

WAKE_UP_POSITION = readListFile(norm_wake_up_path)
REST_POSITION = readListFile(norm_rest_path)
BODY_NAMES = readListFile(norm_body_names_path)
WHEELS_NAMES = readListFile(norm_wheels_names_path)

# ------------------------------ FIXTURES ------------------------------ 

def DCMjointStiffnessON(dcm, joint):
    """
    This method activates the stiffness on the chosen joint.
    """
    DCMgiveValue(dcm, "ClearAll", ["Device/SubDeviceList/" + joint + "/Hardness/Actuator/Value"], [1.0], time_=0)
    

def DCMjointStiffnessOFF(dcm, joint):
    """
    This method disables the stiffness on the chosen joint.
    """
    DCMgiveValue(dcm, "ClearAll", ["Device/SubDeviceList/" + joint + "/Hardness/Actuator/Value"], [0.0], time_=0)


def DCMstiffnessON(dcm):
    """
    This method activates the stiffness on all the robot
    except for the wheels.
    """
    for joint in BODY_NAMES:
        stiffness_key = "Device/SubDeviceList/" + str(joint) +"/Hardness/Actuator/Value"
        dcm.set([stiffness_key, "ClearAll", [[1.0, dcm.getTime(0) ]] ])
    

def DCMstiffnessOFF(dcm):
    """
    This method disables the stiffness on all the robot
    except for the wheels.
    """
    for joint in BODY_NAMES:
        stiffness_key = "Device/SubDeviceList/" + str(joint) +"/Hardness/Actuator/Value"
        dcm.set([stiffness_key, "ClearAll", [[0.0, dcm.getTime(0) ]] ])
    
def DCMwheelstiffnessON(dcm):
    """
    This method activates the stiffness of the wheels.
    """
    for wheel in WHEELS_NAMES:
        stiffness_key = wheel +"/Stiffness/Actuator/Value"
        dcm.set([stiffness_key, "ClearAll", [[1.0, dcm.getTime(0) ]] ])
        
        
def DCMwheelstiffnessOFF(dcm):
    """
    This method disables the stiffness of the wheels.
    """
    for wheel in WHEELS_NAMES:
        stiffness_key = wheel +"/Stiffness/Actuator/Value"
        dcm.set([stiffness_key, "ClearAll", [[0.0, dcm.getTime(0) ]] ])


def DCMwakeUp(dcm):
    """
    Robot wakes up in 3.5 seconds.
    """
    DCMstiffnessON(dcm)
    position_key_list = list()
    for joint in BODY_NAMES:
        position_key = "Device/SubDeviceList/" + joint + "/Position/Actuator/Value"
        position_key_list.append(position_key) 
    for position, key in zip(WAKE_UP_POSITION, position_key_list):
        dcm.set([key, "ClearAll", [[float(position), dcm.getTime(3500) ]] ])
    time.sleep(3.6)
        

def DCMrest(dcm):
    """
    Robot rests in 3.5 seconds.
    """
    position_key_list = list()
    for joint in BODY_NAMES:
        position_key = "Device/SubDeviceList/" + str(joint) + "/Position/Actuator/Value"
        position_key_list.append(position_key)
    for position, key in zip(REST_POSITION, position_key_list):
        dcm.set([key, "ClearAll", [[float(position), dcm.getTime(3500) ]] ])
    time.sleep(3.6)
    DCMstiffnessOFF(dcm)
    DCMwheelstiffnessOFF(dcm)
    

def DCMrotate(dcm, nb_tour):
    """
    Robot rotates on itself nb_tour times.
    """
    r_roue = 0.07
    r_cercle = 0.1762
    theta_tot = (r_cercle/r_roue)*2*math.pi*nb_tour
    t_a = 1.5
    t_f = 1.5
    omega_max = 2.0
    gamma_a = omega_max / t_a
    gamma_f = omega_max / t_f
    t_v = (theta_tot - (0.5*gamma_a*t_a*t_a) - (0.5*gamma_f*t_f*t_f))/omega_max
    print t_v
    t1 = t_a
    t2 = t_a + t_v
    t3 = t2 + t_f
    DCMwheelstiffnessON(dcm)
    time.sleep(0.1)
    for wheel in WHEELS_NAMES:
        wheel_actuator_key = "Device/SubDeviceList/" + wheel +"/Speed/Actuator/Value"
        dcm.set(
        [
            wheel_actuator_key,
            "ClearAll",
            [
                [0.0, dcm.getTime(0) ],
                [omega_max, dcm.getTime(1000 * t1) ],
                [omega_max, dcm.getTime(1000 * t2) ],
                [0.0, dcm.getTime(1000 * t3) ]
            ]
        ]
            )
    
    t_tot = t3 + 1
    time.sleep(t_tot)
    DCMwheelstiffnessOFF(dcm)


def DCMmoveX(dcm, distance):
    """
    The robot goes forward for distance meters. 
    """
    r_roue = 0.07
    if distance > 0:
        omega_max = 5.0
    else:
        omega_max = -5.0
    v_max = r_roue * omega_max
    t_a = 1.5
    t_f = 1.5
    gamma_a = v_max / t_a
    gamma_f = v_max / t_f
    t_v = (distance - (0.5*gamma_a*t_a*t_a) - (0.5*gamma_f*t_f*t_f)) / v_max
    print t_v
    if t_v == 0 or t_v < 0:
        print "trajectoire sans vitesse constante"
    else:
        t1 = t_a
        t2= t_a + t_v
        t3 = t2 + t_f
        
        dcm.set(["WheelFR/Stiffness/Actuator/Value", "ClearAll", [[1.0, dcm.getTime(0) ]] ])
        dcm.set(["WheelFL/Stiffness/Actuator/Value", "ClearAll", [[1.0, dcm.getTime(0) ]] ])
        dcm.set(["WheelB/Stiffness/Actuator/Value", "ClearAll", [[0.0, dcm.getTime(0) ]] ])
        
        dcm.set(
        [
            "Device/SubDeviceList/WheelFR/Speed/Actuator/Value",
            "ClearAll",
            [
                [0.0, dcm.getTime(0) ],
                [-omega_max, dcm.getTime(1000 * t1) ],
                [-omega_max, dcm.getTime(1000 * t2) ],
                [0.0, dcm.getTime(1000 * t3) ]
            ]
        ]
            )
        
        dcm.set(
        [
            "Device/SubDeviceList/WheelFL/Speed/Actuator/Value",
            "ClearAll",
            [
                [0.0, dcm.getTime(0) ],
                [omega_max, dcm.getTime(1000 * t1) ],
                [omega_max, dcm.getTime(1000 * t2) ],
                [0.0, dcm.getTime(1000 * t3) ]
            ]
        ]
            )
        t_tot = t3 + 1
        time.sleep(t_tot)
    

def DCMmoveY(dcm, distance):
    """
    The robot goes on the side for distance meters.
    """
    r_roue = 0.07
    if distance > 0:
        omega_max = 3.0
    else:
        omega_max = -3.0
    v_max = r_roue * omega_max
    t_a = 1.0
    t_f = 1.0
    gamma_a = v_max / t_a
    gamma_f = v_max / t_f
    t_v = (distance - (0.5*gamma_a*t_a*t_a) - (0.5*gamma_f*t_f*t_f)) / v_max
    print t_v
    if t_v == 0 or t_v < 0:
        print "trajectoire sans vitesse constante"
    else:
        t1 = t_a
        t2= t_a + t_v
        t3 = t2 + t_f
        
        dcm.set(["WheelFR/Stiffness/Actuator/Value", "ClearAll", [[1.0, dcm.getTime(0) ]] ])
        dcm.set(["WheelFL/Stiffness/Actuator/Value", "ClearAll", [[1.0, dcm.getTime(0) ]] ])
        dcm.set(["WheelB/Stiffness/Actuator/Value", "ClearAll", [[1.0, dcm.getTime(0) ]] ])
        
        dcm.set(
        [
            "Device/SubDeviceList/WheelFR/Speed/Actuator/Value",
            "ClearAll",
            [
                [0.0, dcm.getTime(0) ],
                [-omega_max/2, dcm.getTime(1000 * t1) ],
                [-omega_max/2, dcm.getTime(1000 * t2) ],
                [0.0, dcm.getTime(1000 * t3) ]
            ]
        ]
            )
        
        dcm.set(
        [
            "Device/SubDeviceList/WheelFL/Speed/Actuator/Value",
            "ClearAll",
            [
                [0.0, dcm.getTime(0) ],
                [-omega_max/2, dcm.getTime(1000 * t1) ],
                [-omega_max/2, dcm.getTime(1000 * t2) ],
                [0.0, dcm.getTime(1000 * t3) ]
            ]
        ]
            )
        
        dcm.set(
        [
            "Device/SubDeviceList/WheelB/Speed/Actuator/Value",
            "ClearAll",
            [
                [0.0, dcm.getTime(0) ],
                [omega_max, dcm.getTime(1000 * t1) ],
                [omega_max, dcm.getTime(1000 * t2) ],
                [0.0, dcm.getTime(1000 * t3) ]
            ]
        ]
            )
        t_tot = t3 + 1
        time.sleep(t_tot)
        DCMwheelstiffnessOFF(dcm)
        

def DCMgiveValue(dcm, kindOfUpdate, key_list, value_list, time_):
    """
    Joint control. Arguments are a list of ALMemory keys and an other list
    containing the values you want to be reached in time_ seconds.
    The kind of update has to be chosen, Cf. DCM API. "ClearAll", "Merge", "ClearAfter", "ClearBefore".
    """
    for value, key in zip(value_list, key_list):
        dcm.set([key, kindOfUpdate, [[value, dcm.getTime(1000 * time_) ]] ])
    time.sleep(time_)
    

def DCMjointSinusSolicitation(dcm, mem, jointList, periode):
    """
    Joint sinusoidal solicitation.
    Select a list of joint you want to solicite at the same time, and a periode is second.
    To stop the behavior, touch the robot's head (front head sensor).
    """
    if(periode <= 0):
        print("Physically impossible, periode must be positive")
    else:
        amplitudeList = list()
        for joint in jointList:
            dcm.set(["Device/SubDeviceList/" + joint + "/Hardness/Actuator/Value", "ClearAll", [[1.0, dcm.getTime(0) ]] ])
            amp = mem.getData("Device/SubDeviceList/"+joint+"/Position/Actuator/Max")
            amplitudeList.append(float(amp))
    
        zipped = zip(jointList, amplitudeList)
        print zipped
    
        #Loop
        while(mem.getData("Device/SubDeviceList/Head/Touch/Front/Sensor/Value") != 1):
            for (joint, amplitude) in zipped:
                t = time.time()
                consigne = amplitude*math.sin((2*math.pi*t)/float(periode))
                stepTime = dcm.getTime(100)    
                dcm.set(["Device/SubDeviceList/" + joint + "/Position/Actuator/Value", "Merge", [[consigne, stepTime ]] ])
    
        for joint in jointList:    
            dcm.set(["Device/SubDeviceList/" + joint + "/Hardness/Actuator/Value", "ClearAll", [[0.0, dcm.getTime(0) ]] ])
    