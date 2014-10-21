import pytest
import qha_tools
import subdevice


@pytest.fixture(scope="session")
def unstiff_parts(dcm, mem):
    joints = qha_tools.use_section("test_pod.cfg", "Parts")
    for name in joints:
        joint_hardness = subdevice.JointHardnessActuator(dcm, mem, name)
        joint_hardness.qqvalue = 0.
