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


@pytest.fixture(scope="session")
def test_time(request):
    """Test time"""
    return request.config.getoption("--testTime")


@pytest.fixture(scope="session")
def nb_cycles(request):
    """Cycles number"""
    return request.config.getoption("--nbCycles")
