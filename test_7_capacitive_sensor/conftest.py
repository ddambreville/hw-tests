import pytest
import qha_tools
import subdevice
from math import radians

CONFIG_FILE_DETECTION = "sensor_detection.cfg"
CONFIG_FILE_FALSE_POSITIVE = "sensor_false_positive.cfg"

# ------------ Sensor detection fixtures ------------

@pytest.fixture(params=qha_tools.use_section(CONFIG_FILE_DETECTION,
                                             "HeadSensors"))
def location(request):
    """Parametrize head capacitive sensor test."""
    return request.param

@pytest.fixture(params=qha_tools.use_section(CONFIG_FILE_DETECTION,
                                             "HandSensors"))
def hand_sensor(request):
    """Parametrize hand capacitive sensor test."""
    return request.param

@pytest.fixture(scope="module")
def time_to_touch():
    """Defines times user needs to touch capacitive sensor."""
    time_touch = \
    qha_tools.read_parameter(CONFIG_FILE_DETECTION,
                             "GeneralParameters",
                             "TimeToTouch")
    return float(time_touch)

# ------------ Sensor false positive fixtures ------------

@pytest.fixture(scope="module")
def test_time_fp():
    """Defines time hand capacitive sensor false positives are tested."""
    time = \
    qha_tools.read_parameter(CONFIG_FILE_FALSE_POSITIVE,
                             "GeneralParameters",
                             "WristTestTime")
    return float(time)

@pytest.fixture(scope="module")
def front_head_sensor(dcm, mem):
    """Front head sensor python object"""
    return subdevice.HeadTouchSensor(dcm, mem, "Front")

@pytest.fixture(scope="module")
def middle_head_sensor(dcm, mem):
    """Middle head sensor python object"""
    return subdevice.HeadTouchSensor(dcm, mem, "Middle")

@pytest.fixture(scope="module")
def rear_head_sensor(dcm, mem):
    """Rear head sensor python object"""
    return subdevice.HeadTouchSensor(dcm, mem, "Rear")

@pytest.fixture(scope="module")
def left_hand_sensor(dcm, mem):
    """Left hand capacitive sensor python object"""
    return subdevice.HandTouchSensor(dcm, mem, "LHand")

@pytest.fixture(scope="module")
def right_hand_sensor(dcm, mem):
    """Right hand capacitive sensor python object"""
    return subdevice.HandTouchSensor(dcm, mem, "RHand")

@pytest.fixture(scope="module")
def rwristyaw(dcm, mem):
    """RWristYaw python object"""
    return subdevice.Joint(dcm, mem, "RWristYaw")

@pytest.fixture(scope="module")
def lwristyaw(dcm, mem):
    """LWristYaw python object"""
    return subdevice.Joint(dcm, mem, "LWristYaw")

@pytest.fixture(scope="function")
def st_hands(request, kill_motion, dcm, mem, stiffness_on, zero_pos, rest_pos,
             stiffness_off, rwristyaw, lwristyaw):
    """Test Setup and TearDown for hands capacitive sensor false positive"""
    # stiffing body
    subdevice.multiple_set(dcm, mem, stiffness_on, wait=True)

    # going to zero position
    subdevice.multiple_set(dcm, mem, zero_pos, wait=True)

    # defining initial max
    lwristyaw_initial_max = lwristyaw.position.actuator.maximum
    rwristyaw_initial_max = rwristyaw.position.actuator.maximum

    # new max position actuator out of real mechanical stop
    lwristyaw_new_max = lwristyaw_initial_max + radians(10.0)
    rwristyaw_new_max = rwristyaw_initial_max + radians(10.0)

    # setting new max
    lwristyaw.position.actuator.maximum = \
    [[[lwristyaw_new_max, dcm.getTime(0)]], "Merge"]
    rwristyaw.position.actuator.maximum = \
    [[[rwristyaw_new_max, dcm.getTime(0)]], "Merge"]

    # going to new max position
    lwristyaw.position.actuator.qvalue = (lwristyaw_new_max, 4000)
    rwristyaw.position.actuator.qvalue = (rwristyaw_new_max, 4000)

    def fin():
        """Hands capacitive sensor test teardown"""
        # going to rest position
        subdevice.multiple_set(dcm, mem, rest_pos, wait=True)

        # unstiff robot
        subdevice.multiple_set(dcm, mem, stiffness_off, wait=True)

        # setting max to their initial values
        lwristyaw.position.actuator.maximum = \
        [[[lwristyaw_initial_max, dcm.getTime(0)]], "Merge"]
        rwristyaw.position.actuator.maximum = \
        [[[rwristyaw_initial_max, dcm.getTime(0)]], "Merge"]

    request.addfinalizer(fin)


@pytest.fixture(scope="module")
def st_head(request, kill_motion, dcm, mem, stiffness_on, wake_up_pos, rest_pos,
             stiffness_off):
    """Test Setup and TearDown for head capacitive sensor false positive"""
    # stiffing body
    subdevice.multiple_set(dcm, mem, stiffness_on, wait=True)

    # going to zero position
    subdevice.multiple_set(dcm, mem, wake_up_pos, wait=True)

    def fin():
        """Head capacitive sensor test teardown"""
        # going to rest position
        subdevice.multiple_set(dcm, mem, rest_pos, wait=True)

        # unstiff robot
        subdevice.multiple_set(dcm, mem, stiffness_off, wait=True)

    request.addfinalizer(fin)

@pytest.fixture(params=qha_tools.use_section(CONFIG_FILE_FALSE_POSITIVE,
                                             "ExcursionTimes"))
def excursion_time(request):
    """Excursion time for head motion in head sensors false positive test"""
    return float(request.param)

@pytest.fixture(scope="module")
def head_behavior_number():
    """Cycle number for head motion in head sensors false positive test"""
    cycle_number = \
    qha_tools.read_parameter(CONFIG_FILE_FALSE_POSITIVE,
                             "GeneralParameters",
                             "HeadCycleNumber")
    return int(cycle_number)
