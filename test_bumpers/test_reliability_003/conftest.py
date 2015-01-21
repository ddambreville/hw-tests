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


@pytest.fixture(params=qha_tools.use_section("reliability_003.cfg", "Directions"))
def direction(request):
    """
    Direction
    """
    return request.param
