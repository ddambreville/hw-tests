import pytest
import subdevice
import qha_tools
import time

def test_head_sensor_detection(dcm, mem, location, time_to_touch):
    flag_expected = False
    timer = qha_tools.Timer(dcm, time_to_touch)
    sensor = subdevice.HeadTouchSensor(dcm, mem, location)
    print
    print
    print "Touch " + location + " Head sensor"
    while timer.is_time_not_out() and flag_expected is False:
        if sensor.value == 1.0:
            flag_expected = True
    assert flag_expected
    time.sleep(0.2)

def test_hand_sensor_detection(dcm, mem, hand_sensor, time_to_touch):
    flag_expected = False
    timer = qha_tools.Timer(dcm, time_to_touch)
    sensor = subdevice.HandTouchSensor(dcm, mem, hand_sensor)
    print
    print
    print "Touch " + hand_sensor + " sensor"
    while timer.is_time_not_out() and flag_expected is False:
        if sensor.value == 1.0:
            flag_expected = True
    assert flag_expected
    time.sleep(0.2)
