import pytest
import tools
from math import radians
import threading
import time
import subdevice

CONFIG_FILE = "stress_test.cfg"


@pytest.fixture(scope="session")
def joint_list(motion):
    return motion.getBodyNames("Body")


@pytest.fixture(scope="session")
def joint_temperature_object(motion, dcm, mem, joint_list):
    """
    Return a dictionnary of objects related to JointTemperature class from
    subdevice.py
    """
    dico_object = dict()
    for joint in joint_list:
        joint_object = subdevice.JointTemperature(dcm, mem, joint)
        dico_object[joint] = joint_object
    return dico_object


@pytest.fixture(scope="class")
def temperature_logger(request, joint_temperature_object, result_base_folder, ):
    """
    Automatically launch logger at the beggining of the test class.
    """
    print "activating temperature logger..."
    logger = tools.Logger()
    thread_flag = threading.Event()

    def logging(thread_flag):
        """To be commented."""
        while not thread_flag.is_set():
            listeofparams = list()
            for joint_temperature in joint_temperature_object.values():
                new_tuple = \
                    (joint_temperature.header_name,
                     joint_temperature.value)
                listeofparams.append(new_tuple)
            logger.log_from_list(listeofparams)
            time.sleep(5.0)

    my_logger = threading.Thread(target=logging, args=(thread_flag,))
    my_logger.start()

    def fin():
        """Class teardown."""
        # stop logger thread
        thread_flag.set()
        print "logger stoped, saving file..."
        result_file_path = "/".join(
            [result_base_folder, "Temperatures"]) + ".csv"
        logger.log_file_write(result_file_path)

    request.addfinalizer(fin)


@pytest.fixture(scope="session")
def allowed_temperature_emergencies():
    """
    Reads allowed temperature emergencies from configuration file.
    It returns a dictionnary with allowed temperature emergency for each joint.
    """
    print "reading allowed temperature emergencies..."
    return tools.read_section(CONFIG_FILE, "AllowedTemperatureEmergencies")


@pytest.fixture(scope="session")
def body_initial_temperatures(motion, dcm, mem, joint_list):
    """Return a dictionnary corresponding to initial body temperatures."""
    print "reading body initial temperatures..."
    dico_initial_temperatures = {}
    for joint in joint_list:
        joint_temperature = subdevice.JointTemperature(dcm, mem, joint)
        dico_initial_temperatures[joint] = joint_temperature.value

    return dico_initial_temperatures


@pytest.fixture(scope="session")
def offset_protection():
    """
    Offset to protect the robot from its mechanical stops if the calibration
    is not perfect.
    """
    return radians(float(tools.read_parameter(CONFIG_FILE,
                                              "GeneralParameters", "Offset")))


@pytest.fixture(params=tools.use_section("stress_test.cfg", "Tests"))
def test_parameters_dico(request, motion, offset_protection):
    """Parametered behavior."""
    dico = tools.read_section("stress_test.cfg", request.param)
    return dico


@pytest.fixture(scope="session")
def battery_charge(dcm, mem):
    """Returns battery charge object."""
    print "creating battery charge object..."
    return subdevice.BatteryChargeSensor(dcm, mem)


@pytest.fixture(scope="session")
def limit_battery_charge():
    """To commit"""
    return float(tools.read_parameter(CONFIG_FILE, "GeneralParameters",
                                      "LimitBatteryCharge"))


@pytest.fixture(scope="session")
def switch_leds(request, leds):
    """
    Switch off the face leds
    Switch on the ear leds
    """
    print "switching face leds off..."
    leds.off('FaceLeds')
    print "switching ear leds on..."
    leds.on('EarLeds')

    def fin():
        """Leds state as initial configuration."""
        leds.on('FaceLeds')
    request.addfinalizer(fin)


@pytest.fixture(scope="session")
def kill_autonomouslife(autonomous_life):
    """Kill ALAutonomousLife module."""
    try:
        print "killing ALAutonomousLife module..."
        autonomous_life.exit()
    except:
        print "ALAutonomousLife already killed"
