'''
Created on August 22, 2014

@author: amartin
'''

import tools
import pytest
import ConfigParser


@pytest.fixture(scope="session")
def config_test():
    """
    Reading test configuration file
    """
    cfg = ConfigParser.ConfigParser()
    cfg.read('TestConfig.cfg')
    return cfg


@pytest.fixture(params=tools.use_section("TestConfig.cfg", "Dance"))
def dance(request):
    """
    Fixture which return the dance
    """
    return request.param
