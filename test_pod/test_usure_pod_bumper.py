import pytest
import tools
import subdevice
import threading


class RobotMovement(object):

    def __init__(self, dcm, mem):
        self.dcm = dcm
        self.mem = mem
        self.motion = subdevice.WheelsMotion(dcm, mem, 0.15)
        self.wheelfr_temperature_sensor = subdevice.WheelTemperatureSensor(
            dcm, mem, "WheelFR")
        self.wheelfl_temperature_sensor = subdevice.WheelTemperatureSensor(
            dcm, mem, "WheelFL")

        self._back_bumper_sensor = subdevice.Bumper(dcm, mem, "Back")
        self._cycles_done = 0
        self._cycles_with_bumper_ok = 0
        self._list_bumper_nok = []
        self._bumper_blocked_flag = False
        self._loose_connexion_flag = False
        self._stop_cycling_flag = False

    def cycling(self, robot_on_charging_station, timer, nb_cycles):
        """ Cyclage """
        # If the robot is not on the pod, or bumper not activated
        # Test don't start
#        if self._back_bumper_sensor == 0 or\
 #               robot_on_charging_station.value == 0:
  #          print "Put the robot on the pod\nVerify back bumper\n"
   #         self._stop_cycling_flag = True

        while self._stop_cycling_flag == False:
            # Robot moves front
            self._cycles_done += 1
            self.motion.move_x(0.2)
            tools.wait(self.dcm, 7000)
            # Verification of bumper
            if self._back_bumper_sensor.value == 1:
                self._bumper_blocked_flag = True
            else:
                self._bumper_blocked_flag = False

            # Robot moves back
            self.motion.move_x(-0.25)
            tools.wait(self.dcm, 1500)
            # Verification of connexion
            t_init = timer.dcm_time()
            test_time = t_init
            while robot_on_charging_station.value == 1 and test_time < 5000:
                self._loose_connexion_flag = False
                test_time = timer.dcm_time() - t_init
            # If connexion lost
            if test_time < 5000:
                self._loose_connexion_flag = True
            # Verification of bumper
            if self._back_bumper_sensor.value == 1 and\
                self._bumper_blocked_flag == False:
                self._cycles_with_bumper_ok += 1
            else:
                self._list_bumper_nok.append(self._cycles_done)

            # Wait if temperature of wheels too hot
            while self.wheelfr_temperature_sensor.value > 60 or\
                    self.wheelfl_temperature_sensor.value > 60:
                tools.wait(self.dcm, 2000)

            # End if nb_cycles is reached
            if self._cycles_done == nb_cycles:
                self._stop_cycling_flag = True

    def _get_back_bumper_sensor(self):
        return self._back_bumper_sensor.value

    def _get_cycles_done(self):
        return self._cycles_done

    def _get_cycles_with_bumper_ok(self):
        return self._cycles_with_bumper_ok

    def _get_bumper_blocked_flag(self):
        return self._bumper_blocked_flag

    def _get_stop_cycling_flag(self):
        return self._stop_cycling_flag

    def _get_loose_connexion_flag(self):
        return self._loose_connexion_flag

    def _set_stop_cycling_flag(self, status):
        self._stop_cycling_flag = bool(status)

    back_bumper_sensor_value = property(_get_back_bumper_sensor)
    cycles_done = property(_get_cycles_done)
    cycles_with_bumper_ok = property(_get_cycles_with_bumper_ok)
    bumper_blocked_flag = property(_get_bumper_blocked_flag)
    loose_connexion_flag = property(_get_loose_connexion_flag)
    stop_cycling_flag = property(
        _get_stop_cycling_flag, _set_stop_cycling_flag)


def test_usure(dcm, mem, rest_pos, kill_motion, stiff_robot, nb_cycles):
    # Objects creation
    robot_on_charging_station = subdevice.ChargingStationSensor(dcm, mem)
    battery_current = subdevice.BatteryCurrentSensor(dcm, mem)
    logger = tools.Logger()

    # Flag initialization
    flag_detection = True
    flag_bumper = True
    flag_keep_connexion = True

    # Going to initial position
    subdevice.multiple_set(dcm, mem, rest_pos, wait=True)

    movement = RobotMovement(dcm, mem)
    timer = tools.Timer(dcm, 10)

    my_behavior = threading.Thread(target=movement.cycling, args=(
        robot_on_charging_station, timer, nb_cycles))
    my_behavior.start()

    # precedent_cycle = 0
    while movement.stop_cycling_flag == False:
        logger.log(
            ("Time", timer.dcm_time() / 1000.),
            ("CyclesDone", movement.cycles_done),
            ("CyclesDoneWithBumperOk", movement.cycles_with_bumper_ok),
            ("BackBumperSensor", movement.back_bumper_sensor_value),
            ("RobotOnChargingStation", robot_on_charging_station.value),
            ("BatteryCurrent", battery_current.value)
        )

        if movement.back_bumper_sensor_value == 1 and\
                movement.bumper_blocked_flag == False and\
                robot_on_charging_station == 0:
            flag_detection = False

        if movement.bumper_blocked_flag == True:
            flag_bumper = False

    if len(movement._list_bumper_nok) > nb_cycles / 100:
        flag_bumper = False

    if movement.loose_connexion_flag == True:
        flag_keep_connexion = False

    movement.stop_cycling_flag = True
    print("Cycles done = " + str(movement.cycles_done))
    print("Cycles done with bumper ok = " +
          str(movement.cycles_with_bumper_ok))
    logger.log_file_write("test_usure_pod_bumper.csv")

    assert flag_detection
    assert flag_bumper
    assert flag_keep_connexion
