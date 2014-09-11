'''
Created on August 22, 2014

@author: amartin
'''

import pytest
import tools
import ConfigParser


@pytest.fixture(scope="session")
def config_test():
    """
    Reading test configuration file
    """
    cfg = ConfigParser.ConfigParser()
    cfg.read('TestConfig.cfg')
    return cfg


@pytest.fixture(params=tools.use_section("TestConfig.cfg", "Horizontal_Side"))
def side(request):
    """
    Fixture which returns the side(s) to be tested
    """
    return request.param
