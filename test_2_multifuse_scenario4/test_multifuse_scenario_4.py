import pytest
import qha_tools
import subdevice
import math
import easy_plot_connection
import logging
import datetime
import time

# Creating log file
DATE = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
logging.basicConfig(
    filename='Results/'+str(DATE)+'.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

@pytest.mark.usefixtures("kill_motion")
class TestMultifuse:

    def test_fuseboard_keys(self, dcm, mem, fuse):
        """
        Assert that for each fuse temperature min and max are corectly set.
        """
        # objects creation
        fuse_temperature = fuse["FuseTemperature"]
        # assertion
        assert fuse_temperature.minimum == 140
        assert fuse_temperature.maximum == 200

    def test_fuseboard_temperature(self, dcm, mem, fuse, wheel_objects,
                                   multi_fuseboard_ambiant_tmp,
                                   multi_fuseboard_total_current,
                                   test_time, joint_limit_extension,
                                   result_base_folder, plot, plot_server):
        """
        If on a fuse max temperature is reached, HAL is supposed to cut the
        stiffness on all the joints behind the considered fuse.
        To add in /media/internal/DeviveInternalHeadGeode.xml before the test:
        <Preference name="Key15"
        memoryName="RobotConfig/Head/MinMaxChangeAllowed" description=""
        value="1" type="string" />
        """
        # logger initialization
        log = logging.getLogger('MULTIFUSEBOARD_PERF_HW_01')

        # erasing real time curves
        if plot:
            plot_server.curves_erase()

        # flag initialization
        flag_loop = True
        flag_key = True
        fuse_state = True
        flag_ambiant_temperature = True
        flag_fuse_status = True
        flag_first_overshoot = False
        flag_protection_on = False

        # flags
        (flag1, flag2, flag3) = (False, False, False)

        # objects creation
        fuse_temperature = fuse["FuseTemperature"]
        fuse_current = fuse["FuseCurrent"]
        fuse_voltage = fuse["FuseVoltage"]
        fuse_resistor = fuse["FuseResistor"]
        battery = subdevice.BatteryChargeSensor(dcm, mem)

        log.info("")
        log.info("***********************************************")
        log.info("Testing fuse : " + str(fuse_temperature.part))
        log.info("***********************************************")
        log.info("")

        # checking that ALMemory key MinMaxChange Allowed = 1
        if int(mem.getData("RobotConfig/Head/MinMaxChangeAllowed")) != 1:
            flag_loop = False
            flag_key = False
            log.error("MinMaxChangeAllowed ALMemory key missing")

        # setting fuse temperature min and max
        fuse_temperature_max = fuse_temperature.maximum
        fuse_temperature_min = fuse_temperature.minimum
        fuse_temperature_mid = (
            fuse_temperature_max + fuse_temperature_min) / 2.

        # setting fuse temperature min and max for hysteresis
        fuse_temperature_max_hyst = fuse_temperature_max - 10
        log.debug("fuse_temperature_max_hyst = "+str(fuse_temperature_max_hyst))
        fuse_temperature_min_hyst = fuse_temperature_min - 10
        log.debug("fuse_temperature_min_hyst = "+str(fuse_temperature_min_hyst))
        fuse_temperature_mid_hyst = fuse_temperature_mid - 10
        log.debug("fuse_temperature_mid_hyst = "+str(fuse_temperature_mid_hyst))

        # position dictionnary creation with normal min or max
        state = \
            qha_tools.read_section(
                "multifuse_scenario4.cfg", fuse_temperature.part)
        # creating joint list
        joint_list = state.keys()
        log.info("Joints to use are : " + str(joint_list))

        # max stiffness is set on all joints except for LegFuse
        if fuse_temperature.part == "LegFuse":
            # stiff joints
            qha_tools.stiff_joints_proportion(dcm, mem, joint_list, 1.0)
            # stiff wheels

            for wheel in wheel_objects:
                wheel.stiffness.qqvalue = 1.0
                wheel.speed.actuator.qvalue = \
                (wheel.speed.actuator.maximum, 5000)
        else:
            qha_tools.stiff_joints_proportion(dcm, mem, joint_list, 1.0)

        # defining increment in radians
        increment = math.radians(joint_limit_extension)

        # modifying max or min position and put the joint in that position
        # it makes current rise a lot
        for joint, value in state.items():
            joint_object = subdevice.JointPositionActuator(dcm, mem, joint)
            if value[0] == 'max':
                new_maximum_angle = joint_object.maximum + increment
            else:
                new_maximum_angle = joint_object.minimum - increment
            joint_object.maximum = [
                [[new_maximum_angle, dcm.getTime(0)]], "Merge"]
            joint_object.qvalue = (new_maximum_angle, 10000)

        # logger creation
        logger = qha_tools.Logger()

        # list object creation
        joint_hardness_list = \
            [subdevice.JointHardnessActuator(dcm, mem, x) for x in joint_list]
        joint_current_list = \
            [subdevice.JointCurrentSensor(dcm, mem, joint)
             for joint in joint_list]

        # loop timer creation
        timer = qha_tools.Timer(dcm, test_time)

        # test loop
        while flag_loop and timer.is_time_not_out():
            try:
                loop_time = timer.dcm_time() / 1000.
                fuse_temperature_status = fuse_temperature.status
                fuse_temperature_value = fuse_temperature.value
                fuse_current_value = fuse_current.value
                fuse_voltage_value = fuse_voltage.value
                fuse_resistor_value = fuse_resistor.value
                fuse_resistor_calculated = fuse_voltage_value / \
                    fuse_current_value
                battery_total_voltage = battery.total_voltage
                multifuseboard_ambiant_tmp = \
                    multi_fuseboard_ambiant_tmp.value
                multifuseboard_total_current = \
                    multi_fuseboard_total_current.value
                stiffness_decrease = mem.getData(
                    "Device/SubDeviceList/FuseProtection/"+\
                    "StiffnessDecrease/Value")
                stiffness_decrease_immediate = mem.getData(
                    "Device/SubDeviceList/FuseProtection/"+\
                    "StiffnessDecreaseImmediate/Value")

                listeofparams = [
                    ("Time", loop_time),
                    ("MultifuseBoardAmbiantTemperature",
                     multifuseboard_ambiant_tmp),
                    ("MultifuseBoardTotalCurrent",
                     multifuseboard_total_current),
                    ("FuseTemperature", fuse_temperature_value),
                    ("FuseCurrent", fuse_current_value),
                    ("FuseVoltage", fuse_voltage_value),
                    ("FuseResistor", fuse_resistor_value),
                    ("FuseResistorCalculated",
                     fuse_resistor_calculated),
                    ("BatteryVoltage", battery_total_voltage),
                    ("Status", fuse_temperature_status),
                    ("StiffnessDecrease", stiffness_decrease),
                    ("StiffnessDecreaseImmediate",
                     stiffness_decrease_immediate),
                    ("FuseTemperatureMin", fuse_temperature_min),
                    ("FuseTemperatureMid", fuse_temperature_mid),
                    ("FuseTemperatureMax", fuse_temperature_max)
                ]
                for joint_hardness in joint_hardness_list:
                    new_tuple = \
                        (joint_hardness.header_name, joint_hardness.value)
                    listeofparams.append(new_tuple)
                for joint_current in joint_current_list:
                    new_tuple = (
                        joint_current.header_name, joint_current.value)
                    listeofparams.append(new_tuple)
                for wheel in wheel_objects:
                    new_tuple = (wheel.short_name+"_Current",
                                 wheel.current.value)
                    listeofparams.append(new_tuple)

                # Logging informations
                logger.log_from_list(listeofparams)

                # for real time plot
                if plot:
                    plot_server.add_point(
                        "MultifuseBoardAmbiantTemperature",
                        loop_time, multifuseboard_ambiant_tmp)
                    plot_server.add_point(
                        "MultifuseBoardTotalCurrent",
                        loop_time, multifuseboard_total_current)
                    plot_server.add_point(
                        "FuseTemperature",
                        loop_time, fuse_temperature_value)
                    plot_server.add_point(
                        "FuseCurrent",
                        loop_time, fuse_current_value)
                    plot_server.add_point(
                        "FuseVoltage",
                        loop_time, fuse_voltage_value)
                    plot_server.add_point(
                        "FuseResistor",
                        loop_time, fuse_resistor_value)
                    plot_server.add_point(
                        "FuseResistorCalculated",
                        loop_time, fuse_resistor_calculated)
                    plot_server.add_point(
                        "BatteryVoltage",
                        loop_time, battery_total_voltage)
                    plot_server.add_point(
                        "Status",
                        loop_time, fuse_temperature_status)
                    plot_server.add_point(
                        "StiffnessDecrease",
                        loop_time, stiffness_decrease)
                    plot_server.add_point(
                        "StiffnessDecreaseImmediate",
                        loop_time, stiffness_decrease_immediate)

                # Checking REQ_FUSE_TEMPERATURE_002
                if fuse_temperature_value < multifuseboard_ambiant_tmp:
                    flag_ambiant_temperature = False
                    log.info("Fuse temperature is lower than MultiFuseBoard" +\
                     "ambiant temperature")

                # Checking REQ_FUSE_PERF_003
                # Fuse status evolves correctly with its estimated temperature
                # Hysteresis works correctly too
                if fuse_temperature_value >= fuse_temperature_min:
                    flag1 = True
                if fuse_temperature_mid < fuse_temperature_value <=\
                 fuse_temperature_max:
                    flag2 = True
                if fuse_temperature_value >= fuse_temperature_max:
                    flag3 = True

                if (flag1, flag2, flag3) == (False, False, False):
                    theorical_status = 0
                elif (flag1, flag2, flag3) == (True, False, False):
                    theorical_status = 1
                elif (flag1, flag2, flag3) == (True, True, False):
                    theorical_status = 2
                elif (flag1, flag2, flag3) == (True, True, True):
                    theorical_status = 3

                if theorical_status == 3 and fuse_temperature_value <=\
                 fuse_temperature_max_hyst:
                    theorical_status = 2
                    flag3 = False
                if theorical_status == 2 and fuse_temperature_value <=\
                 fuse_temperature_mid_hyst:
                    theorical_status = 1
                    flag2 = False
                if theorical_status == 1 and fuse_temperature_value <=\
                 fuse_temperature_min_hyst:
                    theorical_status = 0
                    flag1 = False

                if fuse_temperature_status != theorical_status:
                    log.warning("!!! Fuse status problem !!!")
                    log.info("fuse temperature = " +\
                     str(fuse_temperature_value))
                    log.info("fuse status = " + str(fuse_temperature_status))
                    log.info("fuse theorical status = " + str(theorical_status))
                    flag_fuse_status = False

                # Indicating fuse first max temperature overshoot
                if fuse_temperature_value >= fuse_temperature_max and not\
                flag_first_overshoot:
                    flag_first_overshoot = True
                    log.info("First temperature overshoot")
                    timer_overshoot = qha_tools.Timer(dcm, 200)

                # Indicating that protection worked
                # Set stiffness actuator to 0 to let fuse cool down
                if flag_first_overshoot and timer_overshoot.is_time_out()\
                and not flag_protection_on and\
                (stiffness_decrease_immediate == 0 or\
                stiffness_decrease == 0):
                    log.info("Flag protection ON")
                    flag_protection_on = True
                    log.info("Concerned joints pluggin activated")
                    qha_tools.unstiff_joints(dcm, mem, joint_list)

                # Checking REQ_FUSE_PERF_004
                if flag_first_overshoot and\
                timer_overshoot.is_time_out() and not\
                flag_protection_on:
                    if fuse_temperature.part == "LegFuse":
                        if stiffness_decrease_immediate != 0:
                            fuse_state = False
                            log.warning("LegFuse protection NOK")
                    else:
                        if stiffness_decrease != 0:
                            fuse_state = False
                            log.warning(fuse_temperature.part +\
                             " protection NOK")

                if flag_protection_on and fuse_temperature_value < 80.0:
                    flag_loop = False
                    log.info("End of test, fuse is cold enough")

            except KeyboardInterrupt:
                flag_loop = False  # out of test loop
                log.info("KeyboardInterrupt from user")

        log.info("!!!! OUT OF TEST LOOP !!!!")

        file_name = "_".join([str(fuse_temperature.part), str(fuse_state)])
        result_file_path = "/".join([result_base_folder, file_name]) + ".csv"
        logger.log_file_write(result_file_path)

        # setting original min and max
        log.info("Setting orininal min and max position actuator values...")
        for joint, value in state.items():
            joint_object = subdevice.JointPositionActuator(dcm, mem, joint)
            if value[0] > 0:
                joint_object.maximum = value[0]
                joint_object.qvalue = (joint_object.maximum, 500)
            else:
                joint_object.minimum = value[0]
                joint_object.qvalue = (joint_object.minimum, 500)

        qha_tools.wait(dcm, 200)
        log.info("Unstiff concerned joints")
        qha_tools.unstiff_joints(dcm, mem, joint_list)
        if fuse_temperature.part == "LegFuse":
            for wheel in wheel_objects:
                wheel.speed.actuator.qvalue = (0.0, 3000)
                time.sleep(3.0)
                wheel.stiffness.qqvalue = 0.0

        assert flag_key
        assert fuse_state
        assert flag_fuse_status
        assert flag_ambiant_temperature
