import pytest
import tools
import subdevice
import math


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

    def test_fuseboard_temperature(self, dcm, mem, fuse,
                                   multi_fuseboard_ambiant_tmp,
                                   multi_fuseboard_total_current,
                                   test_time, joint_limit_extension,
                                   result_base_folder):
        """
        If on a fuse max temperature is reached, HAL is supposed to cut the
        stiffness on all the joints behind the considered fuse.
        To add in /media/internal/DeviveInternalHeadGeode.xml before the test:
        <Preference name="Key15"
        memoryName="RobotConfig/Head/MinMaxChangeAllowed" description=""
        value="1" type="string" />
        """
        # flag initialization
        flag = True
        flag_key = True
        fuse_state = True
        flag_ambiant_temperature = True
        flag_fuse_status = True

        # objects creation
        fuse_temperature = fuse["FuseTemperature"]
        fuse_current = fuse["FuseCurrent"]
        fuse_voltage = fuse["FuseVoltage"]
        fuse_resistor = fuse["FuseResistor"]
        battery = subdevice.BatteryChargeSensor(dcm, mem)

        # checking that ALMemory key MinMaxChange Allowed = 1
        if int(mem.getData("RobotConfig/Head/MinMaxChangeAllowed")) != 1:
            flag = False
            flag_key = False
            print "MinMaxChangeAllowed ALMemory key missing"

        # setting fuse temperature min and max
        fuse_temperature_max = fuse_temperature.maximum
        fuse_temperature_min = fuse_temperature.minimum
        fuse_temperature_mid = (
            fuse_temperature_max + fuse_temperature_min) / 2.

        # position dictionnary creation with normal min or max
        state = \
            tools.read_section(
                "multifuse_scenario4.cfg", fuse_temperature.part)
        # creating joint list
        joint_list = state.keys()
        print joint_list
        tools.stiff_joints(dcm, mem, joint_list)

        # defining increment in radians
        increment = math.radians(joint_limit_extension)

        # modifying max or min position and put the joint in that position
        # it makes current rise a lot
        for joint, value in state.items():
            joint_object = subdevice.JointPositionActuator(dcm, mem, joint)
            print value[0]
            if value[0] == 'max':
                print "max"
                new_maximum_angle = joint_object.maximum + increment
            else:
                print "min"
                new_maximum_angle = joint_object.minimum - increment
            joint_object.maximum = [
                [[new_maximum_angle, dcm.getTime(0)]], "Merge"]
            joint_object.qvalue = (new_maximum_angle, 10000)

        # loop timer creation
        timer = tools.Timer(dcm, test_time)

        # logger creation
        logger = tools.Logger()

        # list object creation
        joint_hardness_list = \
            [subdevice.JointHardnessActuator(dcm, mem, x) for x in joint_list]
        joint_current_list = \
            [subdevice.JointCurrentSensor(dcm, mem, joint)
             for joint in joint_list]

        # test loop
        while flag is True:
            try:
                loop_time = timer.dcm_time() / 1000.
                fuse_temperature_status = fuse_temperature.status
                fuse_temperature_value = fuse_temperature.value
                multifuseboard_ambiant_tmp = \
                    multi_fuseboard_ambiant_tmp.value
                stiffness_decrease = mem.getData(
                    "Device/SubDeviceList/BatteryFuse/StiffnessDecrease/Value")
                stiffness_decrease_immediate = mem.getData(
                    "Device/SubDeviceList/BatteryFuse/StiffnessDecreaseImmediate/Value")

                listeofparams = [
                    ("Time", loop_time),
                    ("MultifuseBoardAmbiantTemperature",
                     multifuseboard_ambiant_tmp),
                    ("MultifuseBoardTotalCurrent",
                     multi_fuseboard_total_current.value),
                    ("FuseTemperature", fuse_temperature_value),
                    ("FuseCurrent", fuse_current.value),
                    ("FuseVoltage", fuse_voltage.value),
                    ("FuseResistor", fuse_resistor.value),
                    ("BatteryVoltage", battery.total_voltage),
                    ("Status", fuse_temperature_status),
                    ("StiffnessDecrease", stiffness_decrease),
                    ("StiffnessDecreaseImmediate",
                     stiffness_decrease_immediate)
                ]
                for joint_hardness in joint_hardness_list:
                    new_tuple = \
                        (joint_hardness.header_name, joint_hardness.value)
                    listeofparams.append(new_tuple)
                for joint_current in joint_current_list:
                    new_tuple = (
                        joint_current.header_name, joint_current.value)
                    listeofparams.append(new_tuple)

                # Logging informations
                logger.log_from_list(listeofparams)

                # Checking REQ_FUSE_TEMPERATURE_002
                if fuse_temperature_value <\
                    multifuseboard_ambiant_tmp:
                    flag_ambiant_temperature = False

                # Checking REQ_FUSE_TEMPERATURE_003
                if fuse_temperature_value < fuse_temperature_min and\
                    fuse_temperature_status != 0:
                    flag_fuse_status = False
                elif((fuse_temperature_min < fuse_temperature_value <
                      fuse_temperature_mid) and (fuse_temperature_status != 1)):
                    flag_fuse_status = False
                elif((fuse_temperature_mid < fuse_temperature_value <
                      fuse_temperature_max) and (fuse_temperature_status != 2)):
                    flag_fuse_status = False
                elif((fuse_temperature_value >= fuse_temperature_max) and
                     (fuse_temperature_status != 3)):
                    flag_fuse_status = False

                # Checking REQ_FUSE_PROTECTION_001
                if fuse_temperature_value >= fuse_temperature_max:
                    flag = False
                    if fuse_temperature.part == "DW" and\
                        stiffness_decrease_immediate != 0:
                        fuse_state = False
                    else:
                        if stiffness_decrease != 0:
                            fuse_state = False

            except KeyboardInterrupt:
                flag = False  # out of test loop

        file_name = "_".join([str(fuse_temperature.part), str(fuse_state)])
        result_file_path = "/".join([result_base_folder, file_name]) + ".csv"
        logger.log_file_write(result_file_path)

        # setting original min and max
        for joint, value in state.items():
            joint_object = subdevice.JointPositionActuator(dcm, mem, joint)
            if value[0] > 0:
                joint_object.maximum = value[0]
                joint_object.qvalue = (joint_object.maximum, 500)
            else:
                joint_object.minimum = value[0]
                joint_object.qvalue = (joint_object.minimum, 500)

        tools.wait(dcm, 1000)
        tools.unstiff_joints(dcm, mem, joint_list)

        assert flag_key
        assert fuse_state
        assert flag_fuse_status
        assert flag_ambiant_temperature
