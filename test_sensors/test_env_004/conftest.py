import pytest
import subdevice
import qha_tools


@pytest.fixture(scope="session")
def parameters():
    """
    Return parameters (config file).
    """
    return qha_tools.read_section("env_004.cfg", "TestParameters")


@pytest.fixture(params=qha_tools.use_section("env_004.cfg", "Speed"))
def speed(request):
    """
    Speed
    """
    return float(request.param)


@pytest.fixture(params=qha_tools.use_section("env_004.cfg", "Directions"))
def direction(request):
    """
    Directions
    """
    return str(direction)
