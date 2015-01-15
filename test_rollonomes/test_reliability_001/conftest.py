import pytest
import subdevice
import qha_tools


@pytest.fixture(params=qha_tools.use_section("reliability_001.cfg", "Speed"))
def speed_value(request):
    """
    Speed
    """
    dico_speed = {
        "Speed": float(request.param)
    }
    return dico_speed
