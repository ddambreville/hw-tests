import pytest
import subdevice
import tools


@pytest.fixture(params=tools.use_section("multifuse_scenario4.cfg", "Test"))
def fuse(request, dcm, mem):
    fuse_temperature = subdevice.FuseTemperature(dcm, mem, request.param)
    fuse_current = subdevice.FuseCurrent(dcm, mem, request.param)
    fuse_voltage = subdevice.FuseVoltage(dcm, mem, request.param)
    fuse_resistor = subdevice.FuseResistor(dcm, mem, request.param)
    dico_to_return = {"FuseTemperature": fuse_temperature,
                      "FuseCurrent": fuse_current,
                      "FuseVoltage": fuse_voltage,
                      "FuseResistor": fuse_resistor
                      }
    return dico_to_return


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
        "multifuse_scenario4.cfg",
        "Parameters",
        "TestTime"
    ))


@pytest.fixture(scope="module")
def joint_limit_extension():
    """Give joint limit extension in degrees."""
    return float(tools.read_parameter(
        "multifuse_scenario4.cfg",
        "Parameters",
        "jointLimitExtension"
    ))
