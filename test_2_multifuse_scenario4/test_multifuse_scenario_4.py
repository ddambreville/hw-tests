import tools
import subdevice
import math

@pytest.mark.usefixtures("kill_motion", "stiff_robot")
class TestMultifuseScenario4:
    def test_fuse_board_scenario_4(dcm, mem, rest_pos, fuse_temperature, fuse_current,
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
        fuse_state = True
        flag_motor_tmp = True
        # checking that ALMemory key MinMaxChange Allowed = 1
        if int(mem.getData("RobotConfig/Head/MinMaxChangeAllowed")) != 1:
            flag = False
            print "MinMaxChangeAllowed ALMemory key missing"
        # going to initial position
        subdevice.multiple_set(dcm, mem, rest_pos, wait=True)
        # position dictionnary creation with normal min or max
        state = tools.read_section(
            "multifuse_scenario4.cfg", fuse_temperature.part)
        print state
        # copy previous positions in order to add an increment
        state.copy()
        # put the joints in their original max position
        subdevice.multiple_set(dcm, mem, state, wait=True)
        # defining increment in radians
        increment = math.radians(joint_limit_extension)
        # modifying max or min position and paste in state
        for key, value in state:
            if key not in ("Time",):
                joint = key.split("/")[0]
                joint_object = subdevice.JointPositionActuator(dcm, mem, joint)
                if value == "max":
                    new_maximum_angle = joint_object.maximum + increment
                else:
                    new_maximum_angle = joint_object.minimum - increment
            state[joint+"/Position/Actuator"] = new_maximum_angle
        # current is going to rise in all joints
        print state
        subdevice.multiple_set(dcm, mem, state, wait=False)
        # loop timer creation
        timer = tools.Timer(dcm, test_time)
        # logger creation
        logger = tools.Logger()
        # fuse max temperature initialization
        # fuse_max_temperature = fuse_temperature.maximum
        joint_list = tools.jointlistcreation_from_state(state)
        print joint_list
        # test loop
        while flag is True:
            joint_state = tools.are_there_null_stiffnesses(dcm, mem, joint_list)
            fuse_temperature_status = fuse_temperature.status
            # If the condition is respected, we go out of the loop
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

            logger.log(
                ("Time", timer.dcm_time() / 1000.),
                (multi_fuseboard_ambiant_tmp.header_name,
                 multi_fuseboard_ambiant_tmp.value),
                (multi_fuseboard_total_current.header_name,
                 multi_fuseboard_total_current.value),
                (fuse_temperature.header_name, fuse_temperature.value),
                (fuse_current.header_name, fuse_current.value),
                (fuse_voltage.header_name, fuse_voltage.value),
                ("Status", fuse_temperature.status)
                )

        result_file_path = "/".join(
            [
                result_base_folder,
                "_".join([str(fuse_temperature.part), str(fuse_state)])])+".csv"
        logger.log_file_write(result_file_path)

        assert fuse_state is True
        assert flag_motor_tmp is True
