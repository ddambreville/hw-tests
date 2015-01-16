import pytest
import qha_tools
from naoqi import ALProxy
from qi import Session


@pytest.fixture(scope="session")
def albehaviormanager(robot_ip, port):
    """ Fixture which returns a proxy to ALBehaviorManager module. """
    return ALProxy("ALBehaviorManager", robot_ip, port)


@pytest.fixture(params=qha_tools.use_section(
                "pod_perf_009.cfg", "Behaviors"))
def behaviors(request):
    """
    Behaviors and dances.
    """
    dico_behaviors = {
        "Name": str(request.param)
    }
    return dico_behaviors


@pytest.fixture(scope="session")
def parameters():
    """
    Return parameters (config file).
    """
    return qha_tools.read_section("pod_perf_009.cfg", "TestParameters")


@pytest.fixture(scope="session")
def alleds(robot_ip, port):
    """ Fixture which returns a proxy to ALLeds module."""
    return ALProxy("ALLeds", robot_ip, port)


@pytest.fixture(scope="session")
def packagemanager(robot_ip, port):
    """ Fixture which returns a proxy to PackageManager module."""
    return ALProxy("PackageManager", robot_ip, port)
