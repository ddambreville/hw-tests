import pytest
import qha_tools


@pytest.fixture(params=qha_tools.use_section(
                "reliability_002.cfg", "BehaviorsName"))
def behaviors(request):
    """
    Behaviors and dances.
    """
    dico_behaviors = {
        "Name": str(request.param)
    }
    return dico_behaviors
