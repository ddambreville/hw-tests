import pytest
import tools
import subdevice
import threading
import easy_plot_connection
import time



def test_pod_docking_undocking(dcm, mem, motion, alrecharge):
    robot_on_charging_station = subdevice.ChargingStationSensor(dcm, mem)
    backbumper_sensor = subdevice.Bumper(dcm, mem, "Back")

    stop_cycling_flag = False
    cycles_done = 0

    if robot_on_charging_station.value == 0:
        stop_cycling_flag = True

    else:
        motion.wakeUp()
        print "On the POD, robot wakes up"

    while not stop_cycling_flag:
        alrecharge.leaveStation()
        print "Leave Station"
        alrecharge.goToStation()
        print "Go to station"
        time.sleep(10)
        while not backbumper_sensor.value:
            pass
        print "Bbumper = 1"
        cycles_done += 1
        if cycles_done == 2:
            stop_cycling_flag = True

    motion.rest()
