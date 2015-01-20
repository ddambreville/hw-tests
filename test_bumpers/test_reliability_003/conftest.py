import pytest
import subdevice
import qha_tools
from naoqi import ALProxy


@pytest.fixture(scope="session")
def parameters():
    """
    Return parameters (config file).
    """
    return qha_tools.read_section("reliability_003.cfg", "TestParameters")


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
