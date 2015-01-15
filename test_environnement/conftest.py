import pytest
import subdevice
import qha_tools


@pytest.fixture(scope="session")
def parameters():
    """
    Return parameters (config file).
    """
    return qha_tools.read_section("perf_002.cfg", "TestParameters")
