import pytest
import tools
from math import radians
import threading
import time
import subdevice
import easy_plot_connection

CONFIG_FILE = "stress_test.cfg"


@pytest.fixture(scope="session")
def plot_server():
    """Return object corresponding to easy plot connection server."""
    print "plot_server object initialization..."
    return easy_plot_connection.Server(local_plot=True)


@pytest.fixture(scope="session")
def joint_list(motion):
    """Returns the robot's joint list once per test session."""
    return motion.getBodyNames("Body")


@pytest.fixture(scope="session")
def sa_objects():
    """
    Returns a dictionnary of sliding average objects with the correct number
    of points for each joint.
    It reads the test configuration file.
    """
    sa_nb_points = tools.read_section(CONFIG_FILE, "SlidingAverageNbPoints")
    dico_object = dict()
    for joint, nb_points in sa_nb_points.items():
        dico_object[joint] = tools.SlidingAverage(int(nb_points[0]))
    return dico_object


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


@pytest.fixture(scope="session")
def body_initial_temperatures(dcm, mem, joint_list):
    """Return a dictionnary corresponding to initial body temperatures."""
    print "reading body initial temperatures..."
    dico_initial_temperatures = {}
    for joint in joint_list:
        joint_temperature = subdevice.JointTemperature(dcm, mem, joint)
        dico_initial_temperatures[joint] = joint_temperature.value

    return dico_initial_temperatures


@pytest.fixture(scope="class")
def temperature_logger(
        request, dcm, joint_temperature_object, result_base_folder, sa_objects,
        plot_server, plot):
    """
    @param dcm : proxy to DCM
    @type dcm : object
    @param joint_temperature_object : dictionary of jointTemperature objects
    @type joint_temperature_object : dictionary
    @param result_base_folder : path where logged data are saved
    @type result_base_folder : string
    @param sa_objects : dictionary of sliding average objects with the adapted
                        coefficient pour each joint
    @type sa_objects : dictionary
    @param plot_server : plot server object
    @type plot_server : object
    @param plot : if True, allow real time plot
    @type plot : Booleen

    @returns : Nothing. Automatically launch logger at the beggining of the
    test class and stops it at the end.
    """
    print "activating temperature logger..."
    logger = tools.Logger()
    thread_flag = threading.Event()

    def logging(thread_flag, plot, plot_server):
        """Logging temperatures while the test class is not finished."""
        timer = tools.Timer(dcm, 1000)
        while not thread_flag.is_set():
            loop_time = timer.dcm_time() / 1000.
            list_of_param = [("Time", loop_time)]
            for joint_temperature in joint_temperature_object.values():
                measured_temperature = joint_temperature.value
                sa_object = sa_objects[joint_temperature.short_name]
                temperature_header = joint_temperature.header_name
                temperature_sa_header = temperature_header + "_sa"

                sa_object.point_add(measured_temperature)
                sa_temperature = sa_object.calc()

                new_tuple = (temperature_header, measured_temperature)
                sa_tuple = (temperature_sa_header, sa_temperature)

                list_of_param.append(new_tuple)
                list_of_param.append(sa_tuple)

                # real time plot
                if plot:
                    plot_server.add_point(
                        temperature_sa_header, loop_time, sa_temperature)

            logger.log_from_list(list_of_param)

            time.sleep(5.0)

    my_logger = threading.Thread(
        target=logging, args=(thread_flag, plot, plot_server))
    my_logger.start()

    def fin():
        """
        Class teardown. Executed at the end of test class.
        The logger is stopped and data is saved into a file.
        """
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
def offset_protection():
    """
    @returns : Offset to protect the robot from its mechanical stops if the
               calibration is not perfect.
    @rtype : float

    """
    return radians(float(tools.read_parameter(CONFIG_FILE,
                                              "GeneralParameters", "Offset")))


@pytest.fixture(scope="session")
def ack_nack_ratio():
    """
    @returns : Max nack/ack ratio accepted for the robot board.
    @rtype : float
    """
    return float(tools.read_parameter(CONFIG_FILE, "GeneralParameters",
                                      "AckNackRatio"))


@pytest.fixture(scope="session")
def obstacle_distance():
    """
    @returns : Distance in meters.
    @rtype : float

    If the robot detects an obstacle closer than this distance, it does not
    rotate around itself.
    """
    return (float(tools.read_parameter(CONFIG_FILE,
                                       "GeneralParameters",
                                       "ObstacleDistance")))


@pytest.fixture(params=tools.use_section("stress_test.cfg", "Tests"))
def test_parameters_dico(request, motion, offset_protection):
    """
    @returns : Dictionary of motion parameters
    @rtype : dictionary

    It returns as many dictionaries as arguments in params [len(params)]
    """
    dico = tools.read_section(CONFIG_FILE, request.param)
    return dico


@pytest.fixture(scope="session")
def battery_charge(dcm, mem):
    """
    @returns : BatteryCharge object
    @rtype : object
    """
    print "creating battery charge object..."
    return subdevice.BatteryChargeSensor(dcm, mem)


@pytest.fixture(scope="session")
def limit_battery_charge():
    """
    @returns : Battery minimum state of charde allowed to pass the test.
    @rtype : float
    """
    return float(tools.read_parameter(CONFIG_FILE, "GeneralParameters",
                                      "LimitBatteryCharge"))


@pytest.fixture(scope="session")
def posture_speed_fraction():
    """
    @returns : Speed fraction in order to go to postures.
    @rtype : float
    """
    return float(tools.read_parameter(CONFIG_FILE, "GeneralParameters",
                                      "InitPostureSpeedFraction"))


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


@pytest.fixture(scope="session")
def boards(dcm, mem, joint_list):
    """
    @param dcm : proxy to dcm
    @type  dcm : object
    @param mem : proxy to ALMemory
    @type mem : object
    @param joint_list : list of all robot joints.
    @type joint_list : list

    @returns : List of all the boards liked to the robot joints.
    @rtype : list of strings

    Invoked once per test session.
    """
    boards = list()
    for joint in joint_list:
        joint_current_sensor = subdevice.JointCurrentSensor(dcm, mem, joint)
        joint_board = joint_current_sensor.device
        if joint_board not in boards:
            boards.append(joint_board)
    return boards
