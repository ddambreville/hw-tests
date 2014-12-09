# -*- coding: utf-8 -*-

'''
Created on November 27, 2014

@author: amartin
'''

import pytest
import ConfigParser
import qha_tools
from subdevice import JointPositionActuator, WheelSpeedSensor,\
    JointPositionSensor, JointHardnessActuator,\
    WheelStiffnessActuator, WheelSpeedActuator, JointCurrentSensor
from math import sin, pi
import time

TIME_INIT = 3000


def get_frequence():
    """
    Reading test configuration file
    """
    cfg = ConfigParser.ConfigParser()
    cfg.read('TestConfig.cfg')
    freq = cfg.get('Config', 'frequences')
    list_freq = []
    i = 0
    for numb, each in enumerate(freq):
        if each == " ":
            list_freq.append(freq[i: numb])
            i = numb + 1
        elif numb == len(freq) - 1:
            list_freq.append(freq[i: numb + 1])
            i = numb + 1
    print list_freq

    return list_freq


@pytest.fixture(params=get_frequence())
def period(request, read_cfg):
    """
    Docstring
    """
    numb_period = int(read_cfg.get('Config', 'numb_period'))
    period = 1 / float(request.param)
    return period, numb_period


@pytest.fixture(scope="session")
def constante_ampli_freq(joint_to_test, read_cfg, period):
    """
    Docstring
    """
    if "HipPitch" in joint_to_test:
        const = float(read_cfg.get('Constante_Ampli_freq', 'HipKneePitch'))
        const_freq = const * period[0]
        if const_freq > 0.9:
            return 0.9
        else:
            return const_freq
    else:
        return 0.9


@pytest.fixture(scope="session")
def read_cfg():
    """
    Docstring
    """
    cfg = ConfigParser.ConfigParser()
    cfg.read('TestConfig.cfg')
    return cfg


@pytest.fixture(scope="session")
def joint_to_test():
    '''
    Docstring
    '''
    joints = qha_tools.use_section('TestConfig.cfg', 'Joints')
    if ('HipPitch' in joints and 'KneePitch' not in joints) or \
            ('KneePitch' in joints and 'HipPitch' not in joints):
        raise Exception("Warning", "Le KneePicth et \
        	HipPitch doivent etre acives ensemble")

    return joints


@pytest.fixture(scope="session")
def stiff_joints(request, dcm, mem, joint_to_test):
    '''
    Docstring
    '''
    obj_stiff = []
    for each in joint_to_test:
        if "Wheel" in each:
            obj = WheelStiffnessActuator(dcm, mem, each)
        else:
            obj = JointHardnessActuator(dcm, mem, each)
        obj_stiff.append(obj)
        obj.qqvalue = 1.0

    def fin():
        '''
        Docstring
        '''
        time.sleep(3)
        for each in obj_stiff:
            each.qqvalue = 0.0

    request.addfinalizer(fin)
    return obj_stiff


@pytest.fixture(scope="session")
def amp_off_joints(dcm, mem, joint_to_test):
    '''
    Docstring
    '''
    dico = {}
    for each in joint_to_test:
        if "Wheel" in each:
            obj = WheelSpeedActuator(dcm, mem, each)
        else:
            obj = JointPositionActuator(dcm, mem, each)
        dico[each] = list()
        dico[each].append(float(obj.maximum))
        dico[each].append(float(obj.maximum + obj.minimum) / 2)
        dico[each].append(obj)
        dico[each].append(float(obj.minimum))
    return dico


@pytest.fixture(scope="session")
def init_joint_position(request, amp_off_joints, constante_ampli_freq):
    '''
    Docstring
    '''
    for each in amp_off_joints.keys():
        if each == 'HipPitch':
            amp_off_joints[each][2].qvalue = (
                constante_ampli_freq * amp_off_joints[each][3], TIME_INIT)
        else:
            amp_off_joints[each][2].qvalue = (
                constante_ampli_freq * amp_off_joints[each][0], TIME_INIT)

    time.sleep(4)

    def fin():
        '''
        Docstring
        '''
        for each in amp_off_joints.keys():
            if each == 'HipPitch':
                amp_off_joints[each][2].qvalue = (
                    amp_off_joints[each][3], TIME_INIT)
            else:
                amp_off_joints[each][2].qvalue = (
                    amp_off_joints[each][0], TIME_INIT)

    request.addfinalizer(fin)


@pytest.fixture(scope="session")
def points(amp_off_joints, period, constante_ampli_freq):
    '''
    Docstring
    '''
    dico = {}
    sample_time = period[0] / 100
    if sample_time < 0.01:
        sample_time = 0.01
    for each in amp_off_joints.keys():
        dico[each] = list()
    numb_point = (float(period[0]) / sample_time) * float(period[1])
    tps = period[0] / 4
    for i in range(0, int(numb_point)):
        for each in amp_off_joints.keys():
            if each == 'HipPitch':
                dico[each].append(
                    (float(constante_ampli_freq * amp_off_joints[each][0] *
                           sin((2 * pi * (-tps)) / period[0])
                           + amp_off_joints[each][1]), TIME_INIT + tps * 1000))
            else:
                dico[each].append(
                    (float(constante_ampli_freq * amp_off_joints[each][0] *
                           sin((2 * pi * tps) / period[0])
                           + amp_off_joints[each][1]), TIME_INIT + tps * 1000))
        tps = tps + sample_time
    return dico


@pytest.fixture(scope="session")
def bag_log(dcm, mem, joint_to_test):
    '''
    Docstring
    '''
    bag = qha_tools.Bag(mem)
    for each in joint_to_test:
        if "Wheel" in each:
            bag.add_object(
                each + "_Joint_Actuator", WheelSpeedActuator(dcm, mem, each))
            bag.add_object(
                each + "_Joint_Sensor", WheelSpeedSensor(dcm, mem, each))
        else:
            bag.add_object(
                each + "_Joint_Actuator", JointPositionActuator(dcm, mem, each))
            bag.add_object(
                each + "_Joint_Sensor", JointPositionSensor(dcm, mem, each))
        bag.add_object(
            each + "_Joint_Current", JointCurrentSensor(dcm, mem, each))
    return bag


@pytest.fixture(scope="function")
def logger(request, result_base_folder, period):
    '''
    Docstring
    '''
    logger_joints = qha_tools.Logger()
    frequence = 1 / period[0]

    def fin():
        """Method executed after a joint test."""
        result_file_path = "/".join(
            [
                result_base_folder,
                str(frequence) +
                "_log_joints"
            ]) + ".csv"
        logger_joints.log_file_write(result_file_path)

    request.addfinalizer(fin)
    return logger_joints
