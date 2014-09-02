'''
Created on August 27, 2014

@author: amartin

Angle de la pente fixe - Distantes differentes
'''

import threading

def robot_motion(motion, pos_0, coord, side, config_test):
    """
    Thread which make the robot move
    """
    # On recupere la distance a parcourir dans le fichier de config
    distance = float(config_test.get('Test_Config', 'Distance_Parcours'))
    while abs(motion.getRobotPosition(True)[coord] - pos_0) < distance:
        motion.move(-0.1, 0, 0)


def test_slope(
    dcm, mem, motion, wakeup, side, get_horizontal_x_segments, config_test,
        remove_safety, remove_diagnosis):
    """
    Test function which test the X distance
    of the horizontal lasers
    """
    motion_thread = threading.Thread(target=robot_motion, args=(
        motion, pos_0, coord, side, config_test))
    motion_thread.start()
    logger = record_horizontaux_data(
        get_horizontal_x_segments, motion, side, pos_0, coord, motion_thread,
        config_test)
    result = check_error(logger, config_test)
    assert 'Fail' not in result
