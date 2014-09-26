#-*- coding: iso-8859-15 -*-

'''
Created on September 25, 2014

@author: amartin
'''

import tools
import pytest
from subdevice import Sonar


@pytest.fixture(scope="module")
def get_sonar_objects(request, result_base_folder, dcm, mem):
    """
    Return a dictionary with several objects for
    each X coordinate of all horizontal segments
    """
    dico = {}
    dico["Front_Sonar"] = Sonar(
        dcm, mem, "Front")
    dico["Back_Sonar"] = Sonar(
        dcm, mem, "Back")

    logger = tools.Logger()
    dico["logger"] = logger

    def fin():
        """Method executed after a joint test."""
        result_file_path = "/".join(
            [
                result_base_folder,
                "Sonar_Log"
            ]) + ".csv"
        logger.log_file_write(result_file_path)

    request.addfinalizer(fin)
    return dico
