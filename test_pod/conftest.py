import pytest
import tools
import subdevice


@pytest.fixture(scope="session")
def unstiff_parts(dcm, mem):
    joints = tools.use_section("parts.cfg", "parts")
    for name in joints:
        joint_hardness = subdevice.JointHardnessActuator(dcm, mem, name)
        joint_hardness.qqvalue = 0.
