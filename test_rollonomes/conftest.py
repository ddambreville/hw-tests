import pytest
import qha_tools
from naoqi import ALProxy
from qi import Session


@pytest.fixture(scope="function", autouse=False)
def session(robot_ip, port, request):
    """ Connect a session to a NAOqi """
    ses = Session()
    ses.connect("tcp://" + robot_ip + ":" + str(port))
    return ses


@pytest.fixture(scope="session")
def albehaviormanager(robot_ip, port):
    """ Fixture which returns a proxy to ALBehaviorManager module. """
    return ALProxy("ALBehaviorManager", robot_ip, port)


@pytest.fixture(scope="session")
def motion_wake_up(request, motion):
    """
    Robot wakeUp.
    """
    motion.wakeUp()

    def fin():
        """Method executed after the end of the test."""
        motion.rest()

    request.addfinalizer(fin)


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
