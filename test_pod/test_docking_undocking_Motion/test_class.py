'''
Created on October 17, 2014

@author: amartin
'''


import time
# from math import atan, degrees


class TestPodMotion(object):

    '''
    Class test Pod with ALMotion
    '''

    def __init__(self):
        """
        Initialisation de la class
        """
        self.state = None
        self.leave_station_result = [0, 0]
        self.look_station_result = [0, 0]
        self.move_station_result = [0, 0]
        self.dock_station_result = [0, 0]

    def set_state(self, state):
        '''
        set state
        '''
        self.state = state

    def get_state(self):
        '''
        get state
        '''
        return self.state

    def log_data(self, get_pod_objects, coord, log_file):
        """
        Log data function
        """
        print "log data"
        # if coord[1] == 0:
        #     log_file.write(str(0) + ",")
        # else:
        #     log_file.write(str(degrees(atan(coord[0] / coord[1]))) + ",")
        log_file.write(str(coord[0]) + ",")
        log_file.write(str(get_pod_objects[
            "robot_on_charging_station"].value) + ",")
        log_file.write(str(get_pod_objects[
            "backbumper"].value) + ",")
        log_file.write(str(get_pod_objects[
            "battery_current"].value) + ",")
        log_file.write(str(self.leave_station_result[0]) + "," +
                       str(self.leave_station_result[1]) + "," +
                       str(self.look_station_result[0]) + "," +
                       str(self.look_station_result[1]) + "," +
                       str(self.move_station_result[0]) + "," +
                       str(self.move_station_result[1]) + "," +
                       str(self.dock_station_result[0]) + "," +
                       str(self.dock_station_result[1]) + "\n")
        log_file.flush()
        if get_pod_objects["robot_on_charging_station"].value == 1:
            self.set_state("Arret")
        else:
            self.set_state("Fail")

    def leave_station(self, alrecharge, my_dict):
        """
        Robot leaves POD
        """
        print "leaveStation"
        result = alrecharge.leaveStation()
        print result
        my_dict["leaveStation"].append(result)
        if result == False:
            self.leave_station_result[1] += 1
            self.set_state("leave_motion")
        else:
            self.set_state("move")
            self.leave_station_result[0] += 1
        time.sleep(0.5)

    def leave_motion(self, motion):
        """
        Robot leaves POD
        """
        print "leave_motion"
        motion.moveTo(0.5, 0, 0)
        self.set_state("move")

    def move(self, motion, coord):
        """
        Robot moves away from the POD
        """
        print "move"
        motion.moveTo(coord[0], coord[1], 0, 3)
        time.sleep(0.5)
        self.set_state("lookForStation")

    def look_for_station(self, alrecharge, my_dict):
        """
        Robot looks for POD
        """
        print "lookForStation"
        tab = alrecharge.lookForStation()
        print tab[0]
        my_dict["lookForStation"].append(tab[0])
        if tab[0] == True:
            self.set_state("moveInFrontOfStation")
            self.look_station_result[0] += 1
        else:
            self.set_state("lookForStation")
            self.look_station_result[1] += 1
        time.sleep(0.5)
        return tab[0]

    def move_front_station(self, alrecharge, my_dict):
        """
        Robots moves in front the POD
        """
        print "moveInFrontOfStation"
        result = alrecharge.moveInFrontOfStation()
        print result
        my_dict["moveInFrontOfStation"].append(result)
        if result == True:
            self.set_state("dockOnStation")
            self.move_station_result[0] += 1
        else:
            self.set_state("moveInFrontOfStation")
            self.move_station_result[1] += 1
        time.sleep(0.5)
        return result

    def dock_on_station(self, alrecharge, get_pod_objects, my_dict):
        """
        Robot docks on the POD
        """
        print "dockOnStation"
        result = alrecharge.dockOnStation()
        print result
        time.sleep(0.5)
        my_dict["dockOnStation"].append(result)
        if result == True or get_pod_objects[
                "robot_on_charging_station"].value == 1:
            time.sleep(4)
            self.set_state("log_data")
            self.dock_station_result[0] += 1
        else:
            self.set_state("dockOnStation")
            self.dock_station_result[1] += 1
        return result
