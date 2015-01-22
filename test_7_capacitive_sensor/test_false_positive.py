import qha_tools
from threading import Thread
import capacitive_sensor_utils

def test_hands(st_hands, dcm, left_hand_sensor, right_hand_sensor, test_time_fp):
    timer = qha_tools.Timer(dcm, test_time_fp)
    while timer.is_time_not_out():
        assert left_hand_sensor.value == 0
        assert right_hand_sensor.value == 0

def test_head(dcm, mem, st_head, front_head_sensor, middle_head_sensor,
    rear_head_sensor, excursion_time, head_behavior_number):
    # Thread behavior
    head_behavior = \
    Thread(target=capacitive_sensor_utils.head_behavior,
           args=(dcm, mem, excursion_time, head_behavior_number))
    head_behavior.start()
    flag_result = True

    # test loop
    while head_behavior.isAlive():
        front_value = front_head_sensor.value
        middle_value = middle_head_sensor.value
        rear_value = rear_head_sensor.value
        result_tuple = (front_value, middle_value, rear_value)
        if result_tuple != (0., 0., 0.):
            flag_result = False
    assert flag_result
