import pytest
import tools
import subdevice
import time

@pytest.mark.usefixtures(
    "disable_push_recovery", "disable_arms_external_collisions",
    "disable_fall_manager", "wake_up")
class TestStress:
    def test_1(self, motion):
        print "test 1 in progress..."
        assert motion.robotIsWakeUp()
        time.sleep(1)
    def test_2(self):
        print "test 2 in progress"
        time.sleep(1)
