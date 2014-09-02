import pytest
import tools
import subdevice
import math

@pytest.mark.usefixtures("kill_motion")
class TestMultifuse:
    def test_fuse_board_scenario_4(self, dcm, mem, fuse_temperature, fuse_current,
        fuse_voltage, multi_fuseboard_ambiant_tmp, multi_fuseboard_total_current,
        test_time, joint_limit_extension, result_base_folder):
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
        flag_motor_tmp = True
        # checking that ALMemory key MinMaxChange Allowed = 1
        if int(mem.getData("RobotConfig/Head/MinMaxChangeAllowed")) != 1:
            flag = False
            flag_key = False
            print "MinMaxChangeAllowed ALMemory key missing"
        # position dictionnary creation with normal min or max
        state = \
        tools.read_section("multifuse_scenario4.cfg", fuse_temperature.part)
        # copy previous positions in order to add an increment
        joint_list = tools.jointlistcreation_from_state(state)
        tools.stiff_joints(dcm, mem, joint_list)
        # defining increment in radians
        increment = math.radians(joint_limit_extension)
        # modifying max or min position and put the joint in that position
        for key, value in state.items():
            if key not in ("Time",):
                joint = key.split("/")[0]
                joint_object = subdevice.JointPositionActuator(dcm, mem, joint)
                print value[0]
                if value[0] > 0:
                    new_maximum_angle = joint_object.maximum + increment
                    print "passe par le max"
                else:
                    new_maximum_angle = joint_object.minimum - increment
                    print "passe par le min"
                joint_object.maximum = \
                [[[new_maximum_angle, dcm.getTime(0)]], "Merge"]
                joint_object.qvalue = (new_maximum_angle, 10000)
        # loop timer creation
        timer = tools.Timer(dcm, test_time)
        # logger creation
        logger = tools.Logger()
        # list object creation
        joint_hardness_list = \
        [subdevice.JointHardnessActuator(dcm, mem, x) for x in joint_list]
        joint_current_list = \
        [subdevice.JointCurrentSensor(dcm, mem, joint) for joint in joint_list]
        # test loop
        while flag is True:
            try:
                fuse_temperature_status = fuse_temperature.status
                fuse_temperature_value = fuse_temperature.value
                listeofparams = [
                    ("Time", timer.dcm_time() / 1000.),
                    (multi_fuseboard_ambiant_tmp.header_name,
                     multi_fuseboard_ambiant_tmp.value),
                    (multi_fuseboard_total_current.header_name,
                     multi_fuseboard_total_current.value),
                    (fuse_temperature.header_name, fuse_temperature_value),
                    (fuse_current.header_name, fuse_current.value),
                    (fuse_voltage.header_name, fuse_voltage.value),
                    ("Status", fuse_temperature_status)]
                for joint_hardness in joint_hardness_list:
                    new_tuple = \
                    (joint_hardness.header_name, joint_hardness.value)
                    listeofparams.append(new_tuple)
                for joint_current in joint_current_list:
                    new_tuple = (joint_current.header_name, joint_current.value)
                    listeofparams.append(new_tuple)
                logger.log_from_list(listeofparams)

                # If the condition is respected, we go out of the loop
                joint_state = \
                tools.are_there_null_stiffnesses(dcm, mem, joint_list)
                # Out of the loop if fuse temperature higher than 200 degrees
                # To be removed once REQ_FUSE_TEMPERATURE_003 is OK
                if fuse_temperature_value > 200:
                    flag = False
                if int(fuse_temperature_status) == 3:
                    if tools.is_stiffness_null(dcm, mem, joint_list) is True:
                        flag = False  # we go out of the loop
                    elif tools.is_stiffness_null(dcm, mem, joint_list) is False:
                        flag = False  # we go out of the loop
                        fuse_state = False
                elif int(fuse_temperature_status) < 3:
                    if joint_state[0] is True and \
                    tools.is_stiffness_null(dcm, mem, joint_list) is False:
                        for joint in joint_state[1]:
                            joint_temperature = \
                            subdevice.JointTemperature(dcm, mem, joint)
                            if joint_temperature.value < joint_temperature.maximum:
                                flag = False  # we go out of the loop
                                flag_motor_tmp = False
                    elif tools.is_stiffness_null(dcm, mem, joint_list) is True:
                        flag = False
                        for joint in joint_state[1]:
                            joint_temperature = \
                            subdevice.JointTemperature(dcm, mem, joint)
                            if joint_temperature.value < joint_temperature.maximum:
                                flag_motor_tmp = False
            except KeyboardInterrupt:
                flag = False  # out of test loop

        file_name = "_".join([str(fuse_temperature.part), str(fuse_state)])
        result_file_path = "/".join([result_base_folder, file_name])+".csv"
        logger.log_file_write(result_file_path)

        assert flag_key
        assert fuse_state
        assert flag_motor_tmp
