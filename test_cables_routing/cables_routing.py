import pytest
import subdevice
import time


END = False


def pdc(dcm, mem):
    gyro_x = subdevice.InertialSensorBase(dcm, mem, "GyroscopeX")
    gyro_y = subdevice.InertialSensorBase(dcm, mem, "GyroscopeY")

    passage_de_cables = 0
    minimum = -0.15
    maximum = 0.15

    while not END:
        if gyro_x.value < minimum or gyro_x.value > maximum or\
                gyro_y.value < minimum or gyro_y.value > maximum:
            passage_de_cables += 1
            print("pdc = " + str(passage_de_cables))
            time.sleep(2)

    print("\n\n Nombre de passage de cables = " + str(passage_de_cables))
