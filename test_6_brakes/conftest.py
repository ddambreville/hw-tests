import pytest
import qha_tools
import subdevice
import logging
import math

CONFIG_FILE = "brakes_tests.cfg"

# parametrable values
@pytest.fixture(params=qha_tools.use_section(CONFIG_FILE, "Joint"))
def hc_joint(request):
    """Returns a parametrized joint."""
    return request.param

@pytest.fixture(params=qha_tools.use_section(CONFIG_FILE, "Direction"))
def hc_direction(request):
    """Returns a parametrized direction."""
    return request.param

# Initial angles
@pytest.fixture(scope="module")
def initial_angle():
    """Returns initial angles in degrees"""
    hip_angle_degrees = qha_tools.read_parameter(CONFIG_FILE,
                                                 "GeneralParameters",
                                                 "HipInitialAngle")

    knee_angle_degrees = qha_tools.read_parameter(CONFIG_FILE,
                                                  "GeneralParameters",
                                                  "KneeInitialAngle")
    hip_init_angle_dic = {
        "Positive":-float(hip_angle_degrees),
        "Negative":float(hip_angle_degrees)}
    knee_init_angle_dic = {
        "Positive":-float(knee_angle_degrees),
        "Negative":float(knee_angle_degrees)}

    initial_angle_dict = {
        "HipPitch":hip_init_angle_dic,
        "KneePitch":knee_init_angle_dic}

    return initial_angle_dict

# Angular step
@pytest.fixture(scope="module")
def step():
    hip_step = qha_tools.read_parameter(CONFIG_FILE,
                                        "GeneralParameters",
                                        "HipStep")
    knee_step = qha_tools.read_parameter(CONFIG_FILE,
                                         "GeneralParameters",
                                         "KneeStep")
    step_dict = {
        "HipPitch":float(hip_step),
        "KneePitch":float(knee_step)}

    return step_dict

# Allowed slip number
@pytest.fixture(scope="module")
def allowed_slip_number():
    """Allowed slip number for each couple of joint-direction"""
    slip_number = qha_tools.read_parameter(CONFIG_FILE,
                                           "GeneralParameters",
                                           "AllowedSlipNumber")
    return int(slip_number)

# Wait time
@pytest.fixture(scope="module")
def wait_time():
    """Wait time in seconds in a defined position."""
    to_wait = qha_tools.read_parameter(CONFIG_FILE,
                                       "GeneralParameters",
                                       "WaitTime")
    return float(to_wait)

# Allowed slip angle
@pytest.fixture(scope="module")
def allowed_slip_angle():
    """Allowed slip angle during wait time."""
    slip_angle = qha_tools.read_parameter(CONFIG_FILE,
                                          "GeneralParameters",
                                          "AllowedSlipAngle")
    return float(slip_angle)

# Holding cone
@pytest.fixture(scope="module")
def holding_cone():
    """
    Return all holding cone parameters necessary for tests.
    [Example of use]
    hip_front_max_angle = holding_cone["HipPitch"]["Positive"]
    """
    hip_positive_angle = qha_tools.read_parameter(CONFIG_FILE,
                                                  "ConeCriterion",
                                                  "HipPositive")
    hip_negative_angle = qha_tools.read_parameter(CONFIG_FILE,
                                                  "ConeCriterion",
                                                  "HipNegative")
    knee_positive_angle = qha_tools.read_parameter(CONFIG_FILE,
                                                   "ConeCriterion",
                                                   "KneePositive")
    knee_negative_angle = qha_tools.read_parameter(CONFIG_FILE,
                                                   "ConeCriterion",
                                                   "KneeNegative")
    hip_cone_dic = {"Positive":float(hip_positive_angle),
                    "Negative":float(hip_negative_angle)}
    knee_cone_dic = {"Positive":float(knee_positive_angle),
                     "Negative":float(knee_negative_angle)}

    return {"HipPitch":hip_cone_dic, "KneePitch":knee_cone_dic}

# Joints control
@pytest.fixture(scope="module")
def hippitch(dcm, mem):
    """HipPitch joint as a python object"""
    return subdevice.Joint(dcm, mem, "HipPitch")

@pytest.fixture(scope="module")
def kneepitch(dcm, mem):
    """HipPitch joint as a python object"""
    return subdevice.Joint(dcm, mem, "KneePitch")

@pytest.fixture(scope="module")
def cycle_number():
    """Cycling behavior iteration number."""
    number = qha_tools.read_parameter(CONFIG_FILE,
                                      "CyclingParameters",
                                      "NbCycles")

    return int(number)
