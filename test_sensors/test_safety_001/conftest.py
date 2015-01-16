import pytest
import subdevice
import qha_tools


@pytest.fixture(scope="session")
def parameters():
    """
    Return parameters (config file).
    """
    return qha_tools.read_section("safety_001.cfg", "TestParameters")


@pytest.fixture(params=qha_tools.use_section("safety_001.cfg", "Speed"))
def speed_value(request):
    """
    Speed
    """
    dico_speed = {
        "Speed": float(request.param)
    }
    return dico_speed


@pytest.fixture(params=qha_tools.use_section("safety_001.cfg", "Directions"))
def directions(request):
    """
    Directions
    """
    dico_direction = {
        "Direction": str(request.param)
    }
    return dico_direction


@pytest.fixture(params=qha_tools.use_section(
                "safety_001.cfg", "Dance"))
def behaviors(request):
    """
    Behaviors and dances.
    """
    dico_behaviors = {
        "Name": str(request.param)
    }
    return dico_behaviors
