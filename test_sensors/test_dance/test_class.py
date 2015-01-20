
#-*- coding: iso-8859-15 -*-

'''
Created on December 9, 2014

@author: amartin
'''
import threading
import time


class TestDance(object):

    '''
    Test Dance class
    '''

    def __init__(self, behavior_manager, dance, sensor_objects, cfg):
        self.cfg = cfg
        self.behavior_manager = behavior_manager
        self.dance = dance
        self.logger = sensor_objects["logger_dist"]
        self.logger_e = sensor_objects["logger_error"]
        self.bag = sensor_objects["bag"]
        self.dance_thread = threading.Thread(
            target=self._dance_thread, args=())
        self.result = None

    def _dance_thread(self):
        """
        Dance motion
        """
        apps_list = self.behavior_manager.getBehaviorNames()
        # print apps_list
        dance = "User/" + self.dance
        if dance in apps_list:
            self.behavior_manager.startBehavior(dance)
            while self.behavior_manager.isBehaviorRunning(dance):
                time.sleep(0.5)

    def robot_dance(self):
        '''
        Start dance thread
        '''
        self.dance_thread.start()

    def log(self):
        """
        Record sensors datas
        """
        time_debut = time.time()
        while self.dance_thread.isAlive():
            sensors_value = self.bag.value
            for each in sensors_value.keys():
                self.logger.log((each, sensors_value[each]))
            self.logger.log(("Time", time.time() - time_debut))

    def check_datas(self):
        """
        Check the test result
        """
        self.result = []
        h_sides = ["Front", "Left", "Right"]
        v_sides = ["Left", "Right"]
        s_sides = ["Front", "Back"]
        h_distance = float(self.cfg.get('Distance_Min', 'Horizontal'))
        v_distance = float(self.cfg.get('Distance_Min', 'Vertical'))
        s_distance = float(self.cfg.get('Distance_Min', 'Shovel'))
        so_distance = float(self.cfg.get('Distance_Min', 'Sonar'))
        for side in h_sides:
            for i in range(1, 16):
                for each in self.logger.log_dic["Horizontal_X_seg" + str(i) +
                                                "_" + side]:
                    if each < h_distance:
                        self.result.append('Fail')
                        self.logger_e.log(
                            ("Horizontal_X_seg" + str(i) + "_" + side, each))
                    else:

                        pass

        for side in v_sides:
            for each in self.logger.log_dic["Vertical_X_seg01_" + side]:
                if each < v_distance:
                    self.result.append('Fail')
                    self.logger_e.log(
                        ("Vertical_X_seg01_" + side, each))
        for side in s_sides:
            for each in self.logger.log_dic["Sonar_" + side]:
                if each < so_distance:
                    self.result.append('Fail')
                    self.logger_e.log(
                        ("Sonar_" + side, each))
                else:
                    pass

        for i in range(1, 4):
            for each in self.logger.log_dic["Shovel_X_seg" + str(i)]:
                if each < s_distance:
                    self.result.append('Fail')
                    self.logger_e.log(
                        ("Shovel_X_seg" + str(i), each))
                else:
                    pass

    def print_error(self):
        '''
        Print error on console
        '''
        if 'Fail' in self.result:
            print "NUMBER OF POSITIVES FALSE PER SEGMENT"
            for each in self.logger_e.log_dic.keys():
                print each + ":" + str(len(self.logger_e.log_dic[each]))
        assert 'Fail' not in self.result
