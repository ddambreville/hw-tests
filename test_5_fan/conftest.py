import pytest
import subdevice
import qha_tools


@pytest.fixture(scope="module")
def test_time():
    """It returns the test time in milliseconds [ms]"""
    return int(qha_tools.read_parameter(
        "fan.cfg", "Parameters", "TestTime"))


@pytest.fixture(scope="module")
def cycle_number():
    """It returns the test time in milliseconds [ms]"""
    return int(qha_tools.read_parameter(
        "fan.cfg", "Parameters", "CycleNumber"))


@pytest.fixture(scope="module")
def stop_fans(dcm, mem):
    """
    Tests setup. Fans must be turned off.
    Stop fans and wait 3s.
    """
    fan = subdevice.FanHardnessActuator(dcm, mem)
    fan.qqvalue = 0.0
    qha_tools.wait(dcm, 3000)


@pytest.fixture(scope="module")
def threshold():
    """
    Return a dictionnary corresponding to the threshold speed corresponding
    to half of fan nominal speed.
    """
    left_fan_threshold = int(
        qha_tools.read_parameter("fan.cfg", "Threshold", "LeftFanThreshold"))
    right_fan_threshold = int(
        qha_tools.read_parameter("fan.cfg", "Threshold", "RightFanThreshold"))
    middle_fan_threshold = int(
        qha_tools.read_parameter("fan.cfg", "Threshold", "MiddleFanThreshold"))
    threshold_dict = {
        "LeftFan": left_fan_threshold,
        "RightFan": right_fan_threshold,
        "MiddleFan": middle_fan_threshold
    }
    return threshold_dict
