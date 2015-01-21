import pytest
import qha_tools


@pytest.fixture(params=qha_tools.use_section(
                "pod_perf_009.cfg", "Behaviors"))
def behavior(request):
    """
    Behaviors and dances.
    """
    return str(request.param)


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
