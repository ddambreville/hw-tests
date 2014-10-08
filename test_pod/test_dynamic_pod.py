import pytest
import tools
import subdevice
import threading
import math
import easy_plot_connection
import time


class Plot(threading.Thread):
    """
    Class to log during test
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

        kneepitch_position_actuator = subdevice.JointPositionActuator(
            self.dcm, self.mem, "KneePitch")
        hippitch_position_actuator = subdevice.JointPositionActuator(
            self.dcm, self.mem, "HipPitch")
        hiproll_position_actuator = subdevice.JointPositionActuator(
            self.dcm, self.mem, "HipRoll")
        kneepitch_position_sensor = subdevice.JointPositionSensor(
            self.dcm, self.mem, "KneePitch")
        hippitch_position_sensor = subdevice.JointPositionSensor(
            self.dcm, self.mem, "HipPitch")
        hiproll_position_sensor = subdevice.JointPositionSensor(
            self.dcm, self.mem, "HipRoll")
        kneepitch_temperature = subdevice.JointTemperature(
            self.dcm, self.mem, "KneePitch")
        hippitch_temperature = subdevice.JointTemperature(
            self.dcm, self.mem, "HipPitch")
        hiproll_temperature = subdevice.JointTemperature(
            self.dcm, self.mem, "HipRoll")

        log_file = open(self.file_name, 'w')
        log_file.write(
            "Time,Detection,Current,KneePitchPositionActuator," +
            "KneePitchPositionSensor,KneePitchTemperature," +
            "HipPitchPositionActuator,HipPitchPositionSensor," +
            "HipPitchTemperature,HipRollPositionActuator," +
            "HipRollPositionSensor,HipRollTemperature,WheelBStiffness," +
            "WheelFRStiffness,WheelFLStiffness\n"
        )

        plot_server = easy_plot_connection.Server()

        time_init = time.time()
        while not self._end_plot:
            elapsed_time = time.time() - time_init

            plot_server.add_point(
                "Detection", elapsed_time, robot_on_charging_station.value)
            plot_server.add_point(
                "Current", elapsed_time, battery_current.value)

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

    def stop(self):
        """ To stop logging """
        self._end_plot = True


class DetectionDuringMovement(threading.Thread):
    """
    Class to log data only when robot moves
    """
    def __init__(self, dcm, mem, timer,
                 log_file_name, log_detection_file_name):
        threading.Thread.__init__(self)
        self.dcm = dcm
        self.mem = mem
        self.timer = timer
        self.log_file_name = log_file_name
        self.log_detection_file_name = log_detection_file_name

        self._cycling_stop_flag = False
        self._flag_test = True

    def set_cycling_stop_flag_false(self):
        """ False when robot moves """
        self._cycling_stop_flag = False

    def set_cycling_stop_flag_true(self):
        """True when robot doesn't move """
        self._cycling_stop_flag = True

    def _set_flag_test(self, boolean):
        """ True if test working, else false """
        self._flag_test = bool(boolean)


    def run(self):
        """
        Log only when robot moves
        """
        # Objects creation
        robot_on_charging_station = subdevice.ChargingStationSensor(
            self.dcm, self.mem)
        battery_current = subdevice.BatteryCurrentSensor(self.dcm, self.mem)

        test_timer = 0.
        time_delete = 0.

        detection_flag = True

        log_file = open(self.log_file_name, 'w')
        log_file.write("Time,RobotOnChargingStation,BatteryCurrent\n")

        log_detection = open(self.log_detection_file_name, 'w')
        log_detection.write("TimeLostDetection,TimeFindDetection\n")

        while self._flag_test:
            if not self._cycling_stop_flag:
                test_timer = self.timer.dcm_time() - time_delete
                line_to_write = ",".join([
                    str(test_timer / 1000),
                    str(robot_on_charging_station.value),
                    str(battery_current.value)
                ])
                line_to_write += "\n"
                log_file.write(line_to_write)
                log_file.flush()

                if detection_flag == True and \
                        robot_on_charging_station.value == 0:
                    print "Detection lost : " + str(test_timer / 1000)
                    detection_flag = False
                    log_detection.write(str(test_timer / 1000))
                    log_detection.flush()

                if detection_flag == False and \
                        robot_on_charging_station.value == 1:
                    print "Detection found : " + str(test_timer / 1000)
                    detection_flag = True
                    log_detection.write("," + str(test_timer / 1000) + "\n")
                    log_detection.flush()

            if self._cycling_stop_flag:
                time_delete = self.timer.dcm_time() - test_timer

        if detection_flag == False:
            log_detection.write("," + str(test_timer / 1000) + "\n")
            log_detection.flush()

        print("\n\nRobot moved during " + str(test_timer / 1000) +
              "seconds\n\n")

    def stop(self):
        """ To stop logging """
        self._flag_test = False

    flag_test = property(_set_flag_test)


def kneepitch_cycling(dcm, mem, max_joint_temperature):
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

    parameters = tools.read_section("test_pod.cfg", "DynamicCycling")

    # Initial position
    hippitch_position_actuator.qvalue = (0.,
        int(parameters["time_go_initial_position"][0]) * 1000)
    hiproll_position_actuator.qvalue = (0.,
        int(parameters["time_go_initial_position"][0]) * 1000)
    tools.wait(dcm, int(parameters["time_go_initial_position"][0]) * 1000)
    hippitch_hardness_actuator.qqvalue = 0.

    while kneepitch_temperature.value < max_joint_temperature:
        kneepitch_position_actuator.qvalue = (
            float(parameters["amplitude_kneepitch"][0]),
            int(parameters["time_movement_kneepitch"][0]) * 1000
        )
        tools.wait(dcm, int(parameters["time_movement_kneepitch"][0]) * 1000)
        kneepitch_position_actuator.qvalue = (
            -float(parameters["amplitude_kneepitch"][0]),
            int(parameters["time_movement_kneepitch"][0]) * 1000
        )
        tools.wait(dcm, int(parameters["time_movement_kneepitch"][0]) * 1000)
        print(str(kneepitch_temperature.value))

        if abs(hippitch_position_sensor.value) > \
                float(parameters["angle_slipping"][0]):
            print "Hippitch slip"
            hippitch_hardness_actuator.qqvalue = 1.
            hippitch_position_actuator.qvalue = (0.,
                int(parameters["time_after_slipping"][0]) * 1000)
            kneepitch_position_actuator.qvalue = (0.,
                int(parameters["time_after_slipping"][0]) * 1000)
            tools.wait(dcm, int(parameters["time_after_slipping"][0]) * 1000)
            hippitch_hardness_actuator.qqvalue = 0.

    kneepitch_position_actuator.qvalue = (0.,
        int(parameters["time_go_initial_position"][0]) * 1000)
    tools.wait(dcm, int(parameters["time_go_initial_position"][0]) * 1000)
    hippitch_hardness_actuator.qqvalue = 1.


def hippitch_cycling(dcm, mem, max_joint_temperature):
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

    parameters = tools.read_section("test_pod.cfg", "DynamicCycling")

    # Initial position
    kneepitch_position_actuator.qvalue = (0.,
        int(parameters["time_go_initial_position"][0]) * 1000)
    hiproll_position_actuator.qvalue = (0.,
        int(parameters["time_go_initial_position"][0]) * 1000)
    tools.wait(dcm, int(parameters["time_go_initial_position"][0]) * 1000)
    kneepitch_hardness_actuator.qqvalue = 0.

    while hippitch_temperature.value < max_joint_temperature:
        hippitch_position_actuator.qvalue = (
            float(parameters["amplitude_hippitch"][0]),
            int(parameters["time_movement_hippitch"][0]) * 1000
        )
        tools.wait(dcm, int(parameters["time_movement_hippitch"][0]) * 1000)
        hippitch_position_actuator.qvalue = (
            -float(parameters["amplitude_hippitch"][0]),
            int(parameters["time_movement_hippitch"][0]) * 1000
        )
        tools.wait(dcm, int(parameters["time_movement_hippitch"][0]) * 1000)
        print(str(hippitch_temperature.value))

        if abs(kneepitch_position_sensor.value) > \
                float(parameters["angle_slipping"][0]):
            print "KneePitch slip"
            kneepitch_hardness_actuator.qqvalue = 1.
            kneepitch_position_actuator.qvalue = (0.,
                int(parameters["time_after_slipping"][0]) * 1000)
            hippitch_position_actuator.qvalue = (0.,
                int(parameters["time_after_slipping"][0]) * 1000)
            tools.wait(dcm, int(parameters["time_after_slipping"][0]) * 1000)
            kneepitch_hardness_actuator.qqvalue = 0.

    hippitch_position_actuator.qvalue = (0.,
        int(parameters["time_go_initial_position"][0]) * 1000)
    tools.wait(dcm, int(parameters["time_go_initial_position"][0]) * 1000)
    kneepitch_hardness_actuator.qqvalue = 1.


def hiproll_cycling(dcm, mem, max_joint_temperature):
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

    parameters = tools.read_section("test_pod.cfg", "DynamicCycling")

    # Initial position
    kneepitch_position_actuator.qvalue = (0.,
        int(parameters["time_go_initial_position"][0]) * 1000)
    hippitch_position_actuator.qvalue = (0.,
        int(parameters["time_go_initial_position"][0]) * 1000)
    tools.wait(dcm, int(parameters["time_go_initial_position"][0]) * 1000)
    kneepitch_hardness_actuator.qqvalue = 0.
    hippitch_hardness_actuator.qqvalue = 0.

    while hiproll_temperature.value < max_joint_temperature:
        hiproll_position_actuator.qvalue = (
            float(parameters["amplitude_hiproll"][0]),
            int(parameters["time_movement_hiproll"][0]) * 1000
        )
        tools.wait(dcm, int(parameters["time_movement_hiproll"][0]) * 1000)
        hiproll_position_actuator.qvalue = (
            -float(parameters["amplitude_hiproll"][0]),
            int(parameters["time_movement_hiproll"][0]) * 1000
        )
        tools.wait(dcm, int(parameters["time_movement_hiproll"][0]) * 1000)
        print(str(hiproll_temperature.value))

        if abs(hippitch_position_sensor.value) > \
                float(parameters["angle_slipping"][0]) or\
                abs(kneepitch_position_sensor.value) > \
                float(parameters["angle_slipping"][0]):
            hiproll_position_actuator.qvalue = (0.,
                int(parameters["time_after_slipping"][0]) * 1000)
            hippitch_hardness_actuator.qqvalue = 1.
            hippitch_position_actuator.qvalue = (0.,
                int(parameters["time_after_slipping"][0]) * 1000)
            hippitch_hardness_actuator.qqvalue = 0.
            kneepitch_hardness_actuator.qqvalue = 1.
            kneepitch_position_actuator.qvalue = (0.,
                int(parameters["time_after_slipping"][0]) * 1000)
            tools.wait(dcm, int(parameters["time_after_slipping"][0]) * 1000)
            kneepitch_hardness_actuator.qqvalue = 0.

    hiproll_position_actuator.qvalue = (0.,
        int(parameters["time_go_initial_position"][0]) * 1000)
    tools.wait(dcm, int(parameters["time_go_initial_position"][0]) * 1000)
    kneepitch_hardness_actuator.qqvalue = 1.
    hippitch_hardness_actuator.qqvalue = 1.


def test_pod_damage(dcm, mem, wake_up_pos, kill_motion, stiff_robot,
                    unstiff_parts):
    """
    Test robot moving in the pod to check damages
    """
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

    # Use plot class
    plot_log = Plot(dcm, mem, parameters["easy_plot_csv_name"][0])
    plot_log.start()

    timer = tools.Timer(dcm, int(parameters["test_time"][0]) * 1000)

    # Use detection during movement class
    log_during_movement = DetectionDuringMovement(
        dcm, mem, timer,
        parameters["log_during_movement_csv_name"][0],
        parameters["lost_detection_csv_name"][0]
    )
    log_during_movement.start()

    if robot_on_charging_station.value == 0:
        print "Put the robot on the robot.\nVerify detection.\n"
        flag = False

    while timer.is_time_not_out() and flag == True:
        # Verify if robot moves
        if cycling_step == 3:
            log_during_movement.set_cycling_stop_flag_true()

        if cycling_flag == 0:
            if kneepitch_temperature.value < \
                    int(parameters["max_joint_temperature"][0]):
                print "KneePitch cycling"
                cycling_step = 0
                log_during_movement.set_cycling_stop_flag_false()
                kneepitch_cycling(dcm, mem,
                                  int(parameters["max_joint_temperature"][0]))
            else:
                cycling_step += 1
            cycling_flag = 1

        elif cycling_flag == 1:
            if hippitch_temperature.value < \
                    int(parameters["max_joint_temperature"][0]):
                print "HipPitch cycling"
                cycling_step = 0
                log_during_movement.set_cycling_stop_flag_false()
                hippitch_cycling(
                    dcm, mem,
                    int(parameters["max_joint_temperature"][0])
                )
            else:
                cycling_step += 1
            cycling_flag = 2
        else:
            if hiproll_temperature.value < \
                    int(parameters["max_joint_temperature"][0]):
                print "HipRoll cycling"
                cycling_step = 0
                log_during_movement.set_cycling_stop_flag_false()
                hiproll_cycling(
                    dcm, mem,
                    int(parameters["max_joint_temperature"][0])
                )
            else:
                cycling_step += 1
            cycling_flag = 0

    plot_log.stop()
    log_during_movement.stop()

    assert flag
