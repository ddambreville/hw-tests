'''
Created on August 22, 2014

@author: amartin
'''

import tools
import pytest

@pytest.fixture(params=tools.use_section("TestConfig.cfg", "Dance"))
def dance(request):
    """
    Fixture which return the dance
    """
    return request.param


@pytest.fixture(scope="session")
def wakeup(request, motion):
    """
    Make the robot wakeUp at the beginning
    of the test and go to rest at the end
    """
    # Remove the rotation due to the Active Diagnosis
    motion.setMotionConfig([["ENABLE_MOVE_API", False]])
    motion.wakeUp()
    motion.setMotionConfig([["ENABLE_MOVE_API", True]])

    def fin():
        """Method automatically executed at the end of the test"""
        motion.rest()
    request.addfinalizer(fin)

