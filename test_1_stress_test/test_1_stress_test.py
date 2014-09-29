import pytest
import tools
import subdevice
import time
from stress_test_utils import *


@pytest.mark.usefixtures("disable_push_recovery",
                         "disable_arms_external_collisions",
                         "disable_fall_manager", "wake_up_rest",
                         "temperature_logger", "body_initial_temperatures",
                         "switch_leds")
class TestStress:

    def test_prod_stress(self, dcm, mem, motion, test_parameters_dico,
                         allowed_temperature_emergencies,
                         body_initial_temperatures, offset_protection,
                         battery_charge, limit_battery_charge, boards):
        motion_explore(motion, test_parameters_dico, offset_protection)
        if no_obstacle_detected(dcm, mem, 0.5):
            rotate(motion)
        cycle_brakes(motion)
        assert check_battery_level(battery_charge, limit_battery_charge)
        assert check_nacks(dcm, mem, boards)
