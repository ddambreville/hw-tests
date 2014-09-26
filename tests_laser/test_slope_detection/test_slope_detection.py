'''
Created on August 27, 2014

@author: amartin

Angle de la pente fixe - Distantes differentes
'''

import threading
from termcolor import colored
import time
import CameraViewer
import os


def robot_motion(motion, pos_0, config_test):
    """
    Thread which make the robot move
    """
    # On recupere la distance a parcourir dans le fichier de config
    distance = float(config_test.get('Test_Config', 'Distance_travel'))
    while abs(motion.getRobotPosition(True)[0] - pos_0) < distance:
        print abs(motion.getRobotPosition(True)[0] - pos_0)
        motion.move(-0.1, 0, 0)


def record_slope_data(
        get_slope_segments, motion, pos_0,
        thread, config_test):
    """
    Function which logs the laser distances
    """
    logger = get_slope_segments["logger"]
    angle = float(config_test.get('Test_Config', 'Angle'))
    offset_front = float(config_test.get('Test_Config', 'Offset_Front'))
    while thread.isAlive():
        logger.log(("robot_pos", abs(
            motion.getRobotPosition(True)[0] - pos_0) + offset_front))
        logger.log(("Left_Inclinaison", get_slope_segments[
            "Left_Inclinaison"].value))
        logger.log(("Left_Distance", get_slope_segments[
            "Left_Distance"].value))
        logger.log(("Right_Inclinaison", get_slope_segments[
            "Right_Inclinaison"].value))
        logger.log(("Right_Distance", get_slope_segments[
            "Right_Distance"].value))
        time.sleep(0.01)
    for i in range(0, len(logger.log_dic["robot_pos"])):
        logger.log(("Erreur_Distance_Left", (abs(
            logger.log_dic["robot_pos"][i] - logger.log_dic[
                "Left_Distance"][i]) / logger.log_dic["robot_pos"][i]) * 100))
        logger.log(("Erreur_Distance_Right", (abs(
            logger.log_dic["robot_pos"][i] - logger.log_dic[
                "Right_Distance"][i]) / logger.log_dic["robot_pos"][i]) * 100))
        logger.log(("Erreur_Inclinaison_Left", (abs(
            angle - logger.log_dic["Left_Inclinaison"][i]) / angle) * 100))
        logger.log(("Erreur_Inclinaison_Right", (abs(
            angle - logger.log_dic["Right_Inclinaison"][i]) / angle) * 100))
    return logger


def print_error(logger, name, error_vl, i):
    """
    Print error message
    """
    print name + " : " + colored("Fail", "red")
    print "Position : " + str(logger.log_dic["robot_pos"][i])
    print "Erreur : " + str(error_vl) + "%"


def check_error(logger, config_test):
    """
    Function which checks the distance error
    at the end of the test
    """
    side = ["Left", "Right"]
    result = []
    tolerance_a = float(
        config_test.get('Test_Config', "Tolerance_angle"))
    tolerance_d = float(
        config_test.get('Test_Config', "Tolerance_distance"))
    print len(logger.log_dic["robot_pos"])
    for each in side:
        for i in range(0, len(logger.log_dic["robot_pos"]) - 1):
            error_d = logger.log_dic["Erreur_Distance_" + each][i]
            if error_d > tolerance_d:
                result.append('Fail')
                print_error(logger, each + "_Distance", error_d, i)
                break
            elif i == len(logger.log_dic["robot_pos"]) - 2:
                result.append('Pass')
                print "Distance" + each + " : " + colored("Pass", "green")
    for each in side:
        for i in range(0, len(logger.log_dic["robot_pos"]) - 1):
            error_a = logger.log_dic["Erreur_Inclinaison_" + each][i]
            if error_a > tolerance_a:
                result.append('Fail')
                print_error(logger, each + "_Inclinaison", error_a, i)
                break
            elif i == len(logger.log_dic["robot_pos"]) - 2:
                result.append('Pass')
                print "Distance" + each + " : " + colored("Pass", "green")

    return result


def save_laser_image(cam, path, thread):
    """
    Save laser images with cameraviewer
    """
    print "hihi"
    i = 0
    while thread.isAlive():
        CameraViewer.save_image(cam, path, str(i))
        print "haha"
        i = i + 1


def test_slope(
    check_error_laser, dcm, mem, motion, wakeup, result_base_folder,
        get_slope_segments, config_test, remove_safety, remove_diagnosis):
    """
    Test function which test the X distance
    of the horizontal lasers
    """
    path = os.path.abspath("./") + "/" + result_base_folder
    #cam = CameraViewer.camera_connect()
    print path
    pos_0 = motion.getRobotPosition(True)[0]
    motion_thread = threading.Thread(target=robot_motion, args=(
        motion, pos_0, config_test))
    # image_thread = threading.Thread(target=save_laser_image, args=(
      #  cam, path, motion_thread))
    motion_thread.start()
    # image_thread.start()
    logger = record_slope_data(
        get_slope_segments, motion, pos_0, motion_thread, config_test)
    result = check_error(logger, config_test)
    # CameraViewer.camera_disconnect(cam)
    assert 'Fail' not in result
