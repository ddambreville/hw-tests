# -*- coding: utf-8 -*-

'''
Created on December 01, 2014

@author: amartin

Script de post traitement
'''

import pandas
import os
from math import pi, log


def get_max_min_zero(list_points):
    '''
    Docstring
    '''
    cpt = 0
    max_min_points = []
    for i, key in enumerate(list_points):
        if i != 0:
            value = float(key)
            value_b = float(list_points[i - 1])
            if value * value_b <= 0 and value > 0:
                maxi = max(list_points[cpt: i])
                mini = min(list_points[cpt: i])
                cpt = i + 1
                max_min_points.append((maxi, mini, i))
    del max_min_points[0]
    del max_min_points[-1]
    return max_min_points


def get_moy_amp(list_points):
    '''
    Docstring
    '''
    cpt = 0
    value = 0.0
    for each in list_points:
        value = value + (each[0] - each[1])
        cpt = cpt + 1
    moy = value / cpt
    return moy


def get_phase(actu, sens, time_value, frequence):
    '''
    Docstring
    '''
    cpt = 0
    value = 0.0
    for i in range(0, len(actu)):
        delta = time_value[actu[i][2]] - time_value[sens[i][2]]
        value = value + delta
        cpt = cpt + 1
    moy = value / cpt
    periode = 1 / float(frequence)
    print periode
    print moy
    phase = ((pi * moy) / periode) * (180 / pi)
    return phase


def correction_offset(actu, sens):
    '''
    Docstring
    '''
    offset = sens[0] - actu[0]
    sens_c = []
    for each in sens:
        sens_c.append(each - offset)
    return sens_c


def get_moy_current(list_current):
    '''
    Docstring
    '''
    cpt = 0
    value = 0
    for each in list_current:
        value = value + float(each)
        cpt = cpt + 1
    moy = value / cpt
    print moy
    return moy


def get_bode_datas(list_csv):
    '''
    Docstring
    '''
    list_bode = []
    for each in list_csv:
        for i, letter in enumerate(each):
            if letter == '_':
                frequence = each[0:i]
                break
        print frequence
        datas = pandas.read_csv(each, delimiter=',')
        Knee_Actu_Value = datas.KneePitch_Joint_Actuator
        Knee_Sens_Value = datas.KneePitch_Joint_Sensor
        Knee_Current = datas.KneePitch_Joint_Current
        Time_Value = datas.Time
        current = get_moy_current(Knee_Current)
        sens_correct = correction_offset(Knee_Actu_Value, Knee_Sens_Value)
        actu_max_min_zero = get_max_min_zero(Knee_Actu_Value)
        sens_max_min_zero = get_max_min_zero(sens_correct)
        actu_moy_amp = get_moy_amp(actu_max_min_zero)
        sens_moy_amp = get_moy_amp(sens_max_min_zero)
        phase = get_phase(
            actu_max_min_zero, sens_max_min_zero, Time_Value, frequence)
        list_bode.append(
            [frequence, log(sens_moy_amp / actu_moy_amp, 20), phase, current])

    list_bode_sort = sorted(list_bode)
    return list_bode_sort


def main():
    """
    main
    """
    path = os.path.abspath("./")
    list_path = os.listdir(path)
    list_csv = [p for p in list_path if p.find('.csv') > -1]
    print list_csv
    with open(path + "/Bode.csv", "w") as file_bode:
        file_bode.write("Frequence,Gain,Phase,Current\n")
        list_bode = get_bode_datas(list_csv)
        for each in list_bode:
            file_bode.write(
                each[0] + "," + str(each[1]) + "," +
                str(each[2]) + "," + str(each[3]) + "\n")


if __name__ == '__main__':
    main()
