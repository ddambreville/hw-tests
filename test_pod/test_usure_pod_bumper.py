import pytest
import tools
import subdevice
import threading


def test_usure(dcm, mem, rest_pos, kill_motion, stiff_robot, nb_cycles):
    # Objects creation
    motion = subdevice.WheelsMotion(dcm, mem, 0.15)

    robot_on_charging_station = subdevice.ChargingStationSensor(dcm, mem)
    wheelfr_temperature_sensor = subdevice.WheelTemperatureSensor(
        dcm, mem, "WheelFR")
    wheelfl_temperature_sensor = subdevice.WheelTemperatureSensor(
        dcm, mem, "WheelFL")
    back_bumper_sensor = subdevice.Bumper(dcm, mem, "Back")

    cycles_done = 0
    cycles_with_bumper_ok = 0
    list_bumper_nok = []
    unlock_bumper_status = 0
    bumper_blocked_flag = False
    detection = 1
    loose_connexion_flag = 0
    stop_cycling_flag = False

    # Flag initialization
    flag_detection = True
    flag_bumper = True
    flag_keep_connexion = True

    # Going to initial position
    subdevice.multiple_set(dcm, mem, rest_pos, wait=True)
    timer = tools.Timer(dcm, 10)
    data = open("test_usure_pod_bumper.csv", 'w')
    data.write(
        "CyclesDone,CyclesDoneWithBumperOk," +
        "Detection,LooseConnexion,UnlockBumperStatus,LockBumperStatus\n"
    )

    # Cyclage
    # If the robot is not on the pod or bumper not activated, test don't start
    if back_bumper_sensor.value == 0 or robot_on_charging_station.value == 0:
        print "Put the robot on the pod\nVerify back bumper\n"
        stop_cycling_flag = True
        flag_detection = False
        flag_bumper = False
        flag_keep_connexion = False

    while stop_cycling_flag == False:
        # Robot moves front
        cycles_done += 1
        motion.move_x(0.2)
        tools.wait(dcm, 5000)
        unlock_bumper_status = back_bumper_sensor.value
        # Verification of bumper
        if back_bumper_sensor.value == 1:
            bumper_blocked_flag = True
        else:
            bumper_blocked_flag = False

        # Robot moves back
        motion.move_x(-0.25)
        tools.wait(dcm, 500)
        # Verification of connexion
        t_init = timer.dcm_time()
        test_time = 0
        while robot_on_charging_station.value == 1 and test_time < 5000:
            detection = 1
            loose_connexion_flag = 0
            test_time = timer.dcm_time() - t_init
        # If no detection
        if test_time == 0:
            detection = 0
        # If connexion is lost
        elif test_time < 5000:
            loose_connexion_flag = 1
            flag_keep_connexion = False
        # Verification of bumper
        if back_bumper_sensor.value == 1 and bumper_blocked_flag == False:
            cycles_with_bumper_ok += 1
        else:
            list_bumper_nok.append(cycles_done)

        # Log data
        line_to_write = str(cycles_done) + "," +\
            str(cycles_with_bumper_ok) + "," +\
            str(detection) + "," +\
            str(loose_connexion_flag) + "," +\
            str(unlock_bumper_status) + "," +\
            str(back_bumper_sensor.value) + "\n"
        data.write(line_to_write)

        # Wait if temperature of wheels too hot
        while wheelfr_temperature_sensor.value > 60 or\
                wheelfl_temperature_sensor.value > 60:
            tools.wait(dcm, 2000)

        # End if nb_cycles is reached
        if cycles_done == nb_cycles:
            stop_cycling_flag = True

    if len(list_bumper_nok) > nb_cycles / 100:
        flag_bumper = False

    data.close()
    print("Cycles done = " + str(cycles_done))
    print("Cycles done with bumper ok = " + str(cycles_with_bumper_ok))

    assert flag_detection
    assert flag_bumper
    assert flag_keep_connexion
