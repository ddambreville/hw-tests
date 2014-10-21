import pytest
import qha_tools
import subdevice
import threading
import easy_plot_connection
import time


class Plot(threading.Thread):
    """
    Class to log during test.
    """
    def __init__(self, dcm, mem, file_name):
        threading.Thread.__init__(self)
        self.dcm = dcm
        self.mem = mem
        self.file_name = file_name
        self._end_plot = False

    def run(self):
        """ Log """
        robot_on_charging_station = subdevice.ChargingStationSensor(
            self.dcm, self.mem)
        battery_current = subdevice.BatteryCurrentSensor(self.dcm, self.mem)

        back_bumper_sensor = subdevice.Bumper(self.dcm, self.mem, "Back")

        wheelfr_speed_actuator = subdevice.WheelSpeedActuator(
            self.dcm, self.mem, "WheelFR")
        wheelfl_speed_actuator = subdevice.WheelSpeedActuator(
            self.dcm, self.mem, "WheelFL")
        wheelfr_speed_sensor = subdevice.WheelSpeedSensor(
            self.dcm, self.mem, "WheelFR")
        wheelfl_speed_sensor = subdevice.WheelSpeedSensor(
            self.dcm, self.mem, "WheelFL")
        wheelfr_current_sensor = subdevice.WheelCurrentSensor(
            self.dcm, self.mem, "WheelFR")
        wheelfl_current_sensor = subdevice.WheelCurrentSensor(
            self.dcm, self.mem, "WheelFL")

        log_file = open(self.file_name, 'w')
        log_file.write(
            "Time,Detection,Current,BackBumper,WheelFRSpeedActuator," +
            "WheelFRSpeedSensor,WheelFRCurrent,WheelFLSpeedActuator," +
            "WheelFLSpeedSensor,WheelFLCurrent\n"
        )

        plot_server = easy_plot_connection.Server()

        time_init = time.time()
        while not self._end_plot:
            elapsed_time = time.time() - time_init

            plot_server.add_point(
                "Detection", elapsed_time, robot_on_charging_station.value)
            plot_server.add_point(
                "Current", elapsed_time, battery_current.value)
            plot_server.add_point(
                "BackBumper", elapsed_time, back_bumper_sensor.value)
            plot_server.add_point(
                "WheelFRSpeedActuator", elapsed_time,
                wheelfr_speed_actuator.value)
            plot_server.add_point(
                "WheelFRSpeedSensor", elapsed_time, wheelfr_speed_sensor.value)

            line_to_write = ",".join([
                str(elapsed_time),
                str(robot_on_charging_station.value),
                str(battery_current.value),
                str(back_bumper_sensor.value),
                str(wheelfr_speed_actuator.value),
                str(wheelfr_speed_sensor.value),
                str(wheelfr_current_sensor.value),
                str(wheelfl_speed_actuator.value),
                str(wheelfl_speed_sensor.value),
                str(wheelfl_current_sensor.value)
            ])
            line_to_write += "\n"
            log_file.write(line_to_write)
            log_file.flush()

            time.sleep(0.1)

    def stop(self):
        """ To stop logging """
        self._end_plot = True


def test_damage(dcm, mem, wake_up_pos_brakes_closed, unstiff_parts):
    """
    Test robot docking/undocking to check damages
    """
    # Test parameters
    parameters = qha_tools.read_section("test_pod.cfg", "DockCyclingParameters")

    # Objects creation
    motion = subdevice.WheelsMotion(dcm, mem, float(parameters["speed"][0]))

    robot_on_charging_station = subdevice.ChargingStationSensor(dcm, mem)
    wheelfr_temperature_sensor = subdevice.WheelTemperatureSensor(
        dcm, mem, "WheelFR")
    wheelfl_temperature_sensor = subdevice.WheelTemperatureSensor(
        dcm, mem, "WheelFL")
    back_bumper_sensor = subdevice.Bumper(dcm, mem, "Back")

    # Internal flags
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

    timer = qha_tools.Timer(dcm, 10)
    log_file = open(parameters["cycling_cvs_name"][0], 'w')
    log_file.write(
        "CyclesDone,CyclesDoneWithBumperOk," +
        "Detection,LooseConnection,UnlockBumperStatus,LockBumperStatus\n"
    )

    plot_log = Plot(dcm, mem, parameters["easy_plot_csv_name"][0])
    plot_log.start()

    # Cyclage
    # If the robot is not on the pod or bumper not activated, test don't start
    if robot_on_charging_station.value == 0:
        print "Put the robot on the pod\n"
        stop_cycling_flag = True
        flag_detection = False
        flag_bumper = False
        flag_keep_connexion = False

    while stop_cycling_flag == False:
        # Robot moves front
        cycles_done += 1
        motion.move_x(float(parameters["distance_front"][0]))
        qha_tools.wait(dcm, int(parameters["time_wait_out_the_pod"][0]) * 1000)
        unlock_bumper_status = back_bumper_sensor.value
        # Verification of bumper
        if back_bumper_sensor.value == 1:
            bumper_blocked_flag = True
        else:
            bumper_blocked_flag = False

        # Robot moves back
        motion.move_x(float(parameters["distance_back"][0]))
        motion.stiff_wheels(
            ["WheelFR", "WheelFL", "WheelB"],
            float(parameters["stiffness_wheels_value"][0])
        )
        qha_tools.wait(
            dcm,
            float(parameters["time_wait_before_verify_detection"][0]) * 1000
        )
        # Verification of connexion
        t_init = timer.dcm_time()
        test_time = 0
        while robot_on_charging_station.value == 1 and\
                test_time < int(parameters["time_wait_in_the_pod"][0]) * 1000:
            detection = 1
            loose_connexion_flag = 0
            test_time = timer.dcm_time() - t_init
        # If no detection
        if test_time == 0:
            detection = 0
        # If connexion is lost
        elif test_time < int(parameters["time_wait_in_the_pod"][0]) * 1000:
            loose_connexion_flag = 1
            flag_keep_connexion = False
        # Verification of bumper
        if back_bumper_sensor.value == 1 and bumper_blocked_flag == False:
            cycles_with_bumper_ok += 1
        else:
            list_bumper_nok.append(cycles_done)

        # Log data
        line_to_write = ",".join([
            str(cycles_done),
            str(cycles_with_bumper_ok),
            str(detection),
            str(loose_connexion_flag),
            str(unlock_bumper_status),
            str(back_bumper_sensor.value)
        ])
        line_to_write += "\n"
        log_file.write(line_to_write)
        log_file.flush()

        # Wait if temperature of wheels too hot
        while wheelfr_temperature_sensor.value > \
                int(parameters["wheels_temperature_limit"][0]) or\
                wheelfl_temperature_sensor.value > \
                int(parameters["wheels_temperature_limit"][0]):
            qha_tools.wait(dcm, int(parameters["time_wait_wheels cooled"][0]))

        # End if nb_cycles is reached
        if cycles_done == int(parameters["nb_cycles"][0]):
            stop_cycling_flag = True

    if len(list_bumper_nok) > cycles_done / 100:
        flag_bumper = False

    log_file.close()
    plot_log.stop()
    print("Cycles done = " + str(cycles_done))
    print("Cycles done with bumper ok = " + str(cycles_with_bumper_ok))

    assert flag_detection
    assert flag_bumper
    assert flag_keep_connexion
