import pytest
import qha_tools
import subdevice
import easy_plot_connection


@pytest.fixture(params=qha_tools.use_section("test_current_limitation.cfg", "JulietteJoints"))
def joint(request, dcm, mem):
    """
    Create the appropriate objects for each joint.
    """
    return subdevice.Joint(dcm, mem, request.param)


@pytest.fixture(scope="module")
def parameters():
    """It returns the test parameters"""
    test_time = int(qha_tools.read_parameter(
        "test_current_limitation.cfg", "Parameters", "TestTime"))
    test_time_limit = int(qha_tools.read_parameter(
        "test_current_limitation.cfg", "Parameters", "TestTimeLimit"))
    limit_extension = int(qha_tools.read_parameter(
        "test_current_limitation.cfg", "Parameters", "LimitExtension"))
    limit_factor_sup = float(qha_tools.read_parameter(
        "test_current_limitation.cfg", "Parameters", "LimitFactorSup"))
    limit_factor_inf = float(qha_tools.read_parameter(
        "test_current_limitation.cfg", "Parameters", "LimitFactorInf"))
    sa_nb_points = int(qha_tools.read_parameter(
        "test_current_limitation.cfg", "Parameters", "SlidingAverageNbPoints"))

    # creating parameters dictionnary
    dico_to_return = {
        "test_time": test_time,
        "test_time_limit": test_time_limit,
        "limit_extension": limit_extension,
        "limit_factor_sup": limit_factor_sup,
        "limit_factor_inf": limit_factor_inf,
        "sa_nb_points": sa_nb_points
    }

    return dico_to_return


@pytest.fixture(scope="module")
def plot_server():
    return easy_plot_connection.Server(local_plot=True)
