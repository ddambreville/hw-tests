import pytest
import qha_tools
import subdevice
import time
from stress_test_utils import *


@pytest.mark.usefixtures("disable_push_recovery",
                         "disable_arms_external_collisions",
                         "disable_fall_manager", "wake_up_rest",
                         "temperature_logger", "body_initial_temperatures",
                         "switch_leds")
class TestStress:

    def test_prod_stress(self, dcm, mem, motion, robot_posture,
                         test_parameters_dico, allowed_temperature_emergencies,
                         body_initial_temperatures, offset_protection,
                         battery_charge, limit_battery_charge, boards,
                         ack_nack_ratio, obstacle_distance,
                         joint_temperature_object, posture_speed_fraction):
        """Production stress test adapted to pytest framework."""
        go_to_stand_pos(robot_posture, posture_speed_fraction)
        motion_explore(motion, test_parameters_dico, offset_protection)
        if no_obstacle_detected(dcm, mem, obstacle_distance):
            rotate(motion)
        cycle_brakes(motion)
        assert check_battery_level(battery_charge, limit_battery_charge)
        assert check_nacks(dcm, mem, boards, ack_nack_ratio)
        joints_temperature = get_joints_temperature(joint_temperature_object)
        assert no_overheat(
            body_initial_temperatures, joints_temperature,
            allowed_temperature_emergencies)
