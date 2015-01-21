import pytest
import qha_tools


@pytest.fixture(scope="session")
def parameters():
    """
    Return parameters (config file).
    """
    return qha_tools.read_section("perf_003.cfg", "TestParameters")


@pytest.fixture(params=qha_tools.use_section(
                "perf_003.cfg", "BehaviorsName"))
def behavior(request):
    """
    Behaviors and dances.
    """
    return str(request.param)
