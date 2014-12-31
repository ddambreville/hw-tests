import pytest
import qha_tools
from naoqi import ALProxy
from qi import Session



@pytest.fixture(scope="session")
def albehaviormanager(robot_ip, port):
    """ Fixture which returns a proxy to ALBehaviorManager module. """
    return ALProxy("ALBehaviorManager", robot_ip, port)


@pytest.fixture(params=qha_tools.use_section(
                "rollonomes_reliability_002.cfg", "BehaviorsName"))
def behaviors(request):
    """
    Behaviors and dances.
    """
    dico_behaviors = {
        "Name": str(request.param)
    }
    return dico_behaviors
