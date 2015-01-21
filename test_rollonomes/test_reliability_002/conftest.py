import pytest
import qha_tools


@pytest.fixture(params=qha_tools.use_section(
                "reliability_002.cfg", "BehaviorsName"))
def behavior(request):
    """
    Behaviors and dances.
    """
    return str(request.param)
