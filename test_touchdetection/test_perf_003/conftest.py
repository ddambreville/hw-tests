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
def behaviors(request):
    """
    Behaviors and dances.
    """
    dico_behaviors = {
        "Name": str(request.param)
    }
    return dico_behaviors
