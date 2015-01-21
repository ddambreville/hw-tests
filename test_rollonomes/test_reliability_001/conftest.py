import pytest
import subdevice
import qha_tools


@pytest.fixture(params=qha_tools.use_section("reliability_001.cfg", "Speed"))
def speed(request):
    """
    Speed
    """
    return float(request.param)
