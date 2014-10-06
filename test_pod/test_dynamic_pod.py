import pytest
import tools
import subdevice
import threading
import math
import easy_plot_connection
import time


CYCLING_STOP_FLAG = False
FLAG_TEST = True


def plot(dcm, mem, file_name):
    robot_on_charging_station = subdevice.ChargingStationSensor(dcm, mem)
    battery_current = subdevice.BatteryCurrentSensor(dcm, mem)

    kneepitch_position_actuator = subdevice.JointPositionActuator(
        dcm, mem, "KneePitch")
    hippitch_position_actuator = subdevice.JointPositionActuator(
        dcm, mem, "HipPitch")
    hiproll_position_actuator = subdevice.JointPositionActuator(
        dcm, mem, "HipRoll")
    kneepitch_position_sensor = subdevice.JointPositionSensor(
        dcm, mem, "KneePitch")
    hippitch_position_sensor = subdevice.JointPositionSensor(
        dcm, mem, "HipPitch")
    hiproll_position_sensor = subdevice.JointPositionSensor(
        dcm, mem, "HipRoll")
    kneepitch_temperature = subdevice.JointTemperature(dcm, mem, "KneePitch")
    hippitch_temperature = subdevice.JointTemperature(dcm, mem, "HipPitch")
    hiproll_temperature = subdevice.JointTemperature(dcm, mem, "HipRoll")

    log_file = open(file_name, 'w')
    log_file.write(
        "Time,Detection,Current,KneePitchPositionActuator," +
        "KneePitchPositionSensor,KneePitchTemperature," +
        "HipPitchPositionActuator,HipPitchPositionSensor,HipPitchTemperature," +
        "HipRollPositionActuator,HipRollPositionSensor,HipRollTemperature," +
        "WheelBStiffness,WheelFRStiffness,WheelFLStiffness\n"
    )

    plot_server = easy_plot_connection.Server()

    time_init = time.time()
    while FLAG_TEST == True:
        elapsed_time = time.time() - time_init

        plot_server.add_point(
            "Detection", elapsed_time, robot_on_charging_station.value)
        plot_server.add_point("Current", elapsed_time, battery_current.value)

        plot_server.add_point("KneePitchPositionActuator", elapsed_time,
                              kneepitch_position_actuator)
        plot_server.add_point("KneePitchPositionSensor", elapsed_time,
                              kneepitch_position_sensor)
        plot_server.add_point("KneePitchTemperature", elapsed_time,
                              kneepitch_temperature)

        plot_server.add_point("HipPitchPositionActuator", elapsed_time,
                              hippitch_position_actuator)
        plot_server.add_point("HipPitchPositionSensor", elapsed_time,
                              hippitch_position_sensor)
        plot_server.add_point("HipPitchTemperature", elapsed_time,
                              hippitch_temperature)

        plot_server.add_point("HipRollPositionActuator", elapsed_time,
                              hiproll_position_actuator)
        plot_server.add_point("HipRollPositionSensor", elapsed_time,
                              hiproll_position_sensor)
        plot_server.add_point("HipRollTemperature", elapsed_time,
                              hiproll_temperature)

        line_to_write = ",".join([
            str(elapsed_time),
            str(robot_on_charging_station.value),
            str(battery_current.value),
            str(kneepitch_position_actuator.value),
            str(kneepitch_position_sensor.value),
            str(kneepitch_temperature.value),
            str(hippitch_position_actuator.value),
            str(hippitch_position_sensor.value),
            str(hippitch_temperature.value),
            str(hiproll_position_actuator.value),
            str(hiproll_position_sensor.value),
            str(hiproll_temperature.value)
        ])
        line_to_write += "\n"
        log_file.write(line_to_write)
        log_file.flush()

        time.sleep(0.1)


def kneepitch_cycling(dcm, mem, amplitude_kneepitch):
    """ KneePitch cycling"""
    # Objects creation
    kneepitch_position_actuator = subdevice.JointPositionActuator(
        dcm, mem, "KneePitch")
    kneepitch_temperature = subdevice.JointTemperature(
        dcm, mem, "KneePitch")
    hippitch_position_actuator = subdevice.JointPositionActuator(
        dcm, mem, "HipPitch")
    hippitch_position_sensor = subdevice.JointPositionSensor(
        dcm, mem, "HipPitch")
    hippitch_hardness_actuator = subdevice.JointHardnessActuator(
        dcm, mem, "HipPitch")
    hiproll_position_actuator = subdevice.JointPositionActuator(
        dcm, mem, "HipRoll")

    # Initial position
    hippitch_position_actuator.qvalue = (0., 3000)
    hiproll_position_actuator.qvalue = (0., 3000)
    tools.wait(dcm, 3100)
    hippitch_hardness_actuator.qqvalue = 0.

    while kneepitch_temperature.value < 60:
        kneepitch_position_actuator.qvalue = (-amplitude_kneepitch, 2000)
        tools.wait(dcm, 2100)
        kneepitch_position_actuator.qvalue = (amplitude_kneepitch, 2000)
        tools.wait(dcm, 2100)
        print(str(kneepitch_temperature.value))

        if abs(hippitch_position_sensor.value) > 0.1:
            print "Hippitch slip"
            hippitch_hardness_actuator.qqvalue = 1.
            hippitch_position_actuator.qvalue = (0., 1000)
            kneepitch_position_actuator.qvalue = (0., 2000)
            tools.wait(dcm, 3100)
            hippitch_hardness_actuator.qqvalue = 0.

    kneepitch_position_actuator.qvalue = (0., 3000)
    tools.wait(dcm, 3100)
    hippitch_hardness_actuator.qqvalue = 1.


def hippitch_cycling(dcm, mem, amplitude_hippitch):
    """ HipPitch cycling"""
    # Objects creation
    kneepitch_position_actuator = subdevice.JointPositionActuator(
        dcm, mem, "KneePitch")
    kneepitch_position_sensor = subdevice.JointPositionSensor(
        dcm, mem, "KneePitch")
    kneepitch_hardness_actuator = subdevice.JointHardnessActuator(
        dcm, mem, "KneePitch")
    hippitch_position_actuator = subdevice.JointPositionActuator(
        dcm, mem, "HipPitch")
    hippitch_temperature = subdevice.JointTemperature(
        dcm, mem, "HipPitch")
    hiproll_position_actuator = subdevice.JointPositionActuator(
        dcm, mem, "HipRoll")

    # Initial position
    kneepitch_position_actuator.qvalue = (0., 3000)
    hiproll_position_actuator.qvalue = (0., 3000)
    tools.wait(dcm, 3100)
    kneepitch_hardness_actuator.qqvalue = 0.

    while hippitch_temperature.value < 60:
        hippitch_position_actuator.qvalue = (amplitude_hippitch, 2000)
        tools.wait(dcm, 2100)
        hippitch_position_actuator.qvalue = (-amplitude_hippitch, 1000)
        tools.wait(dcm, 1100)
        print(str(hippitch_temperature.value))

        if abs(kneepitch_position_sensor.value) > 0.1:
            print "KneePitch slip"
            kneepitch_hardness_actuator.qqvalue = 1.
            kneepitch_position_actuator.qvalue = (0., 1000)
            hippitch_position_actuator.qvalue = (0., 2000)
            tools.wait(dcm, 3100)
            kneepitch_hardness_actuator.qqvalue = 0.

    hippitch_position_actuator.qvalue = (0., 3000)
    tools.wait(dcm, 3100)
    kneepitch_hardness_actuator.qqvalue = 1.


def hiproll_cycling(dcm, mem, amplitude_hiproll):
    """HipRoll cycling"""
    # Objects creation
    kneepitch_position_actuator = subdevice.JointPositionActuator(
        dcm, mem, "KneePitch")
    kneepitch_position_sensor = subdevice.JointPositionSensor(
        dcm, mem, "KneePitch")
    kneepitch_hardness_actuator = subdevice.JointHardnessActuator(
        dcm, mem, "KneePitch")
    hippitch_position_actuator = subdevice.JointPositionActuator(
        dcm, mem, "HipPitch")
    hippitch_position_sensor = subdevice.JointPositionSensor(
        dcm, mem, "HipPitch")
    hippitch_hardness_actuator = subdevice.JointHardnessActuator(
        dcm, mem, "HipPitch")
    hiproll_position_actuator = subdevice.JointPositionActuator(
        dcm, mem, "HipRoll")
    hiproll_temperature = subdevice.JointTemperature(
        dcm, mem, "HipRoll")

    # Initial position
    kneepitch_position_actuator.qvalue = (0., 3000)
    tools.wait(dcm, 3100)
    hippitch_position_actuator.qvalue = (0., 3000)
    tools.wait(dcm, 3100)
    kneepitch_hardness_actuator.qqvalue = 0.
    hippitch_hardness_actuator.qqvalue = 0.

    while hiproll_temperature.value < 60:
        hiproll_position_actuator.qvalue = (amplitude_hiproll, 1000)
        tools.wait(dcm, 1100)
        hiproll_position_actuator.qvalue = (-amplitude_hiproll, 1000)
        tools.wait(dcm, 1100)
        print(str(hiproll_temperature.value))

        if abs(hippitch_position_sensor.value) > 0.1 or\
            abs(kneepitch_position_sensor.value) > 0.1:
            hiproll_position_actuator.qvalue = (0., 1000)
            tools.wait(dcm, 1100)
            hippitch_hardness_actuator.qqvalue = 1.
            hippitch_position_actuator.qvalue = (0., 2000)
            tools.wait(dcm, 2100)
            hippitch_hardness_actuator.qqvalue = 0.
            kneepitch_hardness_actuator.qqvalue = 1.
            kneepitch_position_actuator.qvalue = (0., 2000)
            tools.wait(dcm, 2100)
            kneepitch_hardness_actuator.qqvalue = 0.

    hiproll_position_actuator.qvalue = (0., 3000)
    tools.wait(dcm, 3100)
    kneepitch_hardness_actuator.qqvalue = 1.
    hippitch_hardness_actuator.qqvalue = 1.


def log_detection_during_movement(dcm, mem, timer, log_file_name,
                                  log_detection_file_name):
    """
    Log only when robot moves
    """
    # Objects creation
    robot_on_charging_station = subdevice.ChargingStationSensor(dcm, mem)
    battery_current = subdevice.BatteryCurrentSensor(dcm, mem)

    test_timer = 0.
    time_delete = 0.

    detection_flag = True

    log_file = open(log_file_name, 'w')
    log_file.write("Time,RobotOnChargingStation,BatteryCurrent\n")

    log_detection = open(log_detection_file_name, 'w')
    log_detection.write("TimeLostDetection,TimeFindDetection\n")

    while FLAG_TEST == True:
        if CYCLING_STOP_FLAG == False:
            test_timer = timer.dcm_time() - time_delete
            line_to_write = ",".join([
                str(test_timer / 1000),
                str(robot_on_charging_station.value),
                str(battery_current.value)
            ])
            line_to_write += "\n"
            log_file.write(line_to_write)
            log_file.flush()

            if detection_flag == True and robot_on_charging_station.value == 0:
                print "Detection lost : " + str(test_timer / 1000)
                detection_flag = False
                log_detection.write(str(test_timer / 1000))
                log_detection.flush()

            if detection_flag == False and robot_on_charging_station.value == 1:
                print "Detection found : " + str(test_timer / 1000)
                detection_flag = True
                log_detection.write("," + str(test_timer / 1000) + "\n")
                log_detection.flush()

        if CYCLING_STOP_FLAG == True:
            time_delete = timer.dcm_time() - test_timer

    if detection_flag == False:
        log_detection.write("," + str(test_timer / 1000) + "\n")
        log_detection.flush()

    print("\n\nRobot moved during " + str(test_timer / 1000) + "seconds\n\n")


def test_pod_damage(dcm, mem, wake_up_pos, kill_motion, stiff_robot, unstiff_parts):
    global CYCLING_STOP_FLAG
    global FLAG_TEST
    # Objects creation
    robot_on_charging_station = subdevice.ChargingStationSensor(dcm, mem)
    kneepitch_temperature = subdevice.JointTemperature(
        dcm, mem, "KneePitch")
    hippitch_temperature = subdevice.JointTemperature(
        dcm, mem, "HipPitch")
    hiproll_temperature = subdevice.JointTemperature(
        dcm, mem, "HipRoll")

    # Test parameters
    parameters = tools.read_section("test_pod.cfg", "DynamicTestParameters")

    motion = subdevice.WheelsMotion(dcm, mem, 0.15)
    motion.stiff_wheels(
        ["WheelFR", "WheelFL", "WheelB"],
        int(parameters["stiffness_wheels_value"][0])
    )

    cycling_flag = 0
    cycling_step = 0

    # Going to initial position
    subdevice.multiple_set(dcm, mem, wake_up_pos, wait=True)

    # Flag initialization
    flag = True

    # Use easy_plot
    plot_log = threading.Thread(
        target=plot,
        args=(dcm, mem, parameters["easy_plot_csv_name"][0])
    )
    plot_log.start()

    timer = tools.Timer(dcm, int(parameters["test_time"][0]) * 1000)

    log_during_movement = threading.Thread(
        target=log_detection_during_movement,
        args=(dcm, mem, timer, parameters["log_during_movement_csv_name"][0],
              parameters["lost_detection_csv_name"][0]
              )
    )
    log_during_movement.start()

    if robot_on_charging_station.value == 1:
        print "Put the robot on the robot.\nVerify detection.\n"
        flag = False

    while timer.is_time_not_out() and flag == True:
        # Verify if robot moves
        if cycling_step == 3:
            CYCLING_STOP_FLAG = True

        if cycling_flag == 0:
            if kneepitch_temperature.value < 60:
                print "KneePitch cycling"
                cycling_step = 0
                CYCLING_STOP_FLAG = False
                kneepitch_cycling(dcm, mem,
                                float(parameters["amplitude_kneepitch"][0]))
            else:
                cycling_step += 1
            cycling_flag = 1

        elif cycling_flag == 1:
            if hippitch_temperature.value < 60:
                print "HipPitch cycling"
                cycling_step = 0
                CYCLING_STOP_FLAG = False
                hippitch_cycling(dcm, mem,
                                float(parameters["amplitude_hippitch"][0]))
            else:
                cycling_step += 1
            cycling_flag = 2
        else:
            if hiproll_temperature.value < 60:
                print "HipRoll cycling"
                cycling_step = 0
                CYCLING_STOP_FLAG = False
                hiproll_cycling(dcm, mem,
                                float(parameters["amplitude_hiproll"][0]))
            else:
                cycling_step += 1
            cycling_flag = 0

    FLAG_TEST = False

    assert flag
