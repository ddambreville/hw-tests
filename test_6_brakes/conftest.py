import pytest
import qha_tools
import subdevice
import logging
import math
import numpy
import os.path
import time

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

@pytest.fixture(scope="module")
def dico_results(request):
    """"""
    dico_result = {
        "HipPitch":{"Positive":[], "Negative":[]},
        "KneePitch":{"Positive":[], "Negative":[]}
    }

    return dico_result

@pytest.fixture(scope="module")
def print_results(request, dico_results, holding_cone):
    joint_list = qha_tools.use_section(CONFIG_FILE, "Joint")
    direction_list = qha_tools.use_section(CONFIG_FILE, "Direction")
    def fin():
        """Results printed at the end of test session."""
        logging.info("")
        logging.info("-"*40)
        logging.info("              TEST REPORT              ")
        logging.info("-"*40)
        logging.info("")
        for joint in joint_list:
            for direction in direction_list:
                result_list_brut = dico_results[joint][direction]
                result_list = [list(x) for x in zip(*result_list_brut)]
                angle_list = result_list[0]
                temperature_list = result_list[1]

                min_value = numpy.amin(numpy.absolute(angle_list))
                average_value = numpy.average(angle_list)
                std_value = numpy.std(angle_list)

                if min_value < abs(float(holding_cone[joint][direction])):
                    test_result = "FAILED"
                else:
                    test_result = "PASSED"

                logging.info("*"*40)
                logging.info("")
                logging.info(" ".join(["Results for",
                                       joint.upper(),
                                       direction.upper()
                                      ]))
                logging.info("Test result       : " + test_result)
                logging.info("Angles array      : " + str(angle_list))
                logging.info("Temperature array : " + str(temperature_list))
                logging.info("Min value         : " + str(min_value))
                logging.info("Average           : " + str(average_value))
                logging.info("Std               : " + str(std_value))
                logging.info("")
        logging.info("-"*40)

    request.addfinalizer(fin)

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

@pytest.fixture(scope="module", autouse=True)
def initialize_logger(result_base_folder):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to info
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # create error file handler and set level to error
    if not os.path.exists(result_base_folder):
        os.makedirs(result_base_folder)
    handler = logging.FileHandler("/".join([
        result_base_folder,
        "holding_cone_logs.txt"
        ]))
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

@pytest.fixture(scope="function")
def wait_between_two_tests(request, dcm, mem, rest_pos, stiffness_on,
                           stiffness_off):
    """Wait between two tests."""
    time_to_wait = qha_tools.read_parameter(CONFIG_FILE,
                                            "GeneralParameters",
                                            "TimeBetweenTwoTests")
    def fin():
        """Wait between two tests."""
        subdevice.multiple_set(dcm, mem, stiffness_on, wait=True)
        subdevice.multiple_set(dcm, mem, rest_pos, wait=True)
        subdevice.multiple_set(dcm, mem, stiffness_off, wait=True)
        logging.info("Waiting " + str(time_to_wait) + " s")
        time.sleep(float(time_to_wait))
    request.addfinalizer(fin)
