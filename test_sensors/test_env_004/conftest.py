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
def speed_value(request):
    """
    Speed
    """
    dico_speed = {
        "Speed": float(request.param)
    }
    return dico_speed


@pytest.fixture(params=qha_tools.use_section("env_004.cfg", "Directions"))
def directions(request):
    """
    Directions
    """
    dico_direction = {
        "Direction": str(request.param)
    }
    return dico_direction
