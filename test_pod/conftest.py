import pytest


def pytest_addoption(parser):
    """Configuration of pytest parsing."""
    parser.addoption(
        "--testTime",
        type=int,
        action="store",
        default=60,
        help="Test time"
    )
    parser.addoption(
        "--nbCycles",
        type=int,
        action="store",
        default=5000,
        help="Cycles number"
    )
    parser.addoption(
        "--fileName",
        action="store",
        default="test_usure_pod.csv",
        help="Output file name"
    )


@pytest.fixture(scope="session")
def test_time(request):
    """Test time"""
    return request.config.getoption("--testTime")


@pytest.fixture(scope="session")
def nb_cycles(request):
    """Cycles number"""
    return request.config.getoption("--nbCycles")

@pytest.fixture(scope="session")
def file_name(request):
    """Output file name"""
    return request.config.getoption("--fileName")
