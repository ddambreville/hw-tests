import pytest
import subdevice
import tools

@pytest.fixture(
    params=tools.use_section("Configuration/multiFuseBoard.cfg", "Test"))
def fuse_temperature(request, dcm, mem):
    """
    Create an object corresponding to fuse temperature sensor for each fuse.
    """
    return subdevice.fuseTemperature(dcm, mem, request.param)

@pytest.fixture(
    params=tools.use_section("Configuration/multiFuseBoard.cfg", "Test"))
def fuse_current(request, dcm, mem):
    """Create an object corresponding to fuse current sensor for each fuse."""
    return subdevice.fuseCurrent(dcm, mem, request.param)

@pytest.fixture(
    params=tools.use_section("Configuration/multiFuseBoard.cfg", "Test"))
def fuse_voltage(request, dcm, mem):
    """Create an object corresponding to fuse voltage sensor for each fuse."""
    return subdevice.fuseVoltage(dcm, mem, request.param)

@pytest.fixture(scope="module")
def multi_fuseboard_ambiant_tmp(dcm, mem):
    """Object creation of ambiant temperature sensor."""
    return subdevice.MultiFuseBoardAmbiantTemperature(dcm, mem)

@pytest.fixture(scope="module")
def multi_fuseboard_total_current(dcm, mem):
    """Object creation of total current sensor."""
    return subdevice.MultiFuseBoardTotalCurrent(dcm, mem)

@pytest.fixture(scope="module")
def test_time():
    """Give test time."""
    return int(tools.read_parameter(
        "Configuration/jointCurrentSensors.cfg",
        "Parameters",
        "TestTime"
        ))

@pytest.fixture(scope="module")
def joint_limit_extension():
    """Give joint limit extension in degrees."""
    return float(tools.read_parameter(
        "Configuration/jointCurrentSensors.cfg",
        "Parameters",
        "jointLimitExtension"
        ))


