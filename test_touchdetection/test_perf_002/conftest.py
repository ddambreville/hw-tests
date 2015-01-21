import pytest
import subdevice
import qha_tools
from naoqi import ALProxy


@pytest.fixture(scope="session")
def parameters():
    """
    Return parameters (config file).
    """
    return qha_tools.read_section("perf_002.cfg", "TestParameters")


@pytest.fixture(params=qha_tools.use_section("perf_002.cfg", "SpeedRotation"))
def speed_value(request):
    """
    Speed
    """
    return float(request.param)


@pytest.fixture(scope="session")
def remove_sensors(alnavigation):
    """
    Fixture which remove base sensors.
    """
    alnavigation._removeSensor("Laser")
    alnavigation._removeSensor("Sonar")
    alnavigation._removeSensor("Asus")


@pytest.fixture(scope="session")
def alnavigation(robot_ip, port):
    """
    Fixture which returns a proxy to ALNavigation module.
    """
    return ALProxy("ALNavigation", robot_ip, port)


@pytest.fixture(scope="session")
def move_arms_enabled(request, motion):
    """
    Robot can move its arms when it moves base.
    """
    motion.setMoveArmsEnabled(0, 0)

    def fin():
        """Method automatically executed at the end of the test."""
        motion.setMoveArmsEnabled(1, 1)

    request.addfinalizer(fin)
