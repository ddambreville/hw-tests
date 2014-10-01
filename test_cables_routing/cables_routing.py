import pytest
import subdevice
import time


END = False
MAXIMUM = 0.15
MINIMUM = -0.15


def cables_routing(dcm, mem):
    gyro_x = subdevice.InertialSensorBase(dcm, mem, "GyroscopeX")
    gyro_y = subdevice.InertialSensorBase(dcm, mem, "GyroscopeY")

    passage_de_cables = 0

    while not END:
        if gyro_x.value < MINIMUM or gyro_x.value > MAXIMUM or\
                gyro_y.value < MINIMUM or gyro_y.value > MAXIMUM:
            passage_de_cables += 1
            print("pdc = " + str(passage_de_cables))
            time.sleep(2)

    print("\n\n Nombre de passage de cables = " + str(passage_de_cables))
