import tools
import subdevice
import threading
import time
import os
import csv


class BumpersCounting(threading.Thread):
    """
    Class to check the number of bumper activations
    """
    def  __init__(self, dcm, mem, leds, wait_time_bumpers):
        threading.Thread.__init__(self)
        self.dcm = dcm
        self.mem = mem
        self.leds = leds
        self._bumpers_activations = 0
        self.wait_time_bumpers = wait_time_bumpers
        self._stop = threading.Event()

    def stop(self):
        """ stop the thread """
        print "thread bumpers stoppe"
        self._stop.set()

    def _get_bumpers_activations(self):
        """ 
        To get the number of activations
        """
        return self._bumpers_activations

    def run(self):
        bumper_right = subdevice.Bumper(self.dcm, self.mem, "FrontRight")
        bumper_left  = subdevice.Bumper(self.dcm, self.mem, "FrontLeft")
        bumper_back  = subdevice.Bumper(self.dcm, self.mem, "Back")

        list_bumpers = [bumper_right, bumper_left, bumper_back]

        parameters = tools.read_section("config.cfg", "BumpersActivationsParameters")

        # If file already exists, reading to know the previous state
        if os.path.exists(parameters["Log_file_name"][0]):
            data = open(parameters["Log_file_name"][0], 'r')
            csv_reader = csv.reader(data)
            variables_list = []
            row_num = 0
            for row in csv_reader:
                data_num = 0
                if row_num == 0:
                    for value in row:
                        variables_list.append([value])
                else:
                    for value in row:
                        variables_list[data_num].append(value)
                        data_num += 1
                row_num += 1
            self._bumpers_activations = int(variables_list[0][row_num - 1])
            previous_time = float(variables_list[1][row_num - 1])
            data.close()
            data = open(parameters["Log_file_name"][0], 'a')
        # Else initialize to 0
        else:
            self._bumpers_activations = 0
            previous_time = 0.
            data = open(parameters["Log_file_name"][0], 'w')
            data.write("Bumpers activations,Time\n0,0\n")
            data.flush()

        time_init = time.time()

        # Loop
        while not self._stop.is_set():
            for bumper in list_bumpers:
                if bumper.value == 1:
                    self._bumpers_activations += 1
                    data.write(str(self._bumpers_activations) + "," + \
                               str(time.time() - time_init + previous_time) + "\n")
                    print("nb of bumpers activations: " + str(self._bumpers_activations) + "\n")
                    data.flush()
            tools.wait(self.dcm, 2*self.wait_time_bumpers)

    bumpers_activations = property(_get_bumpers_activations)


class CablesCrossing(threading.Thread):
    """
    Class to check the number of cables crossing during a test
    """
    def __init__(self, dcm, mem):
        threading.Thread.__init__(self)
        self.dcm = dcm
        self.mem = mem
        self._cables_crossing = 0
        # self._end_cables_crossing = False
        self._stop = threading.Event()

    def stop(self):
        """ stop the thread """
        print "thread cables stoppe"
        self._stop.set()

    def _get_cables_crossing(self):
        """ To know the number of cables crossing """
        return self._cables_crossing

    def run(self):
        """Log cables crossing"""
        gyro_x = subdevice.InertialSensorBase(self.dcm, self.mem, "GyroscopeX")
        gyro_y = subdevice.InertialSensorBase(self.dcm, self.mem, "GyroscopeY")

        parameters = tools.read_section("config.cfg", "CablesRoutingParameters")

        # If file already exists, reading to know the previous state
        if os.path.exists(parameters["Log_file_name"][0]):
            data = open(parameters["Log_file_name"][0], 'r')
            csv_reader = csv.reader(data)
            variables_list = []
            row_num = 0
            for row in csv_reader:
                data_num = 0
                if row_num == 0:
                    for value in row:
                        variables_list.append([value])
                else:
                    for value in row:
                        variables_list[data_num].append(value)
                        data_num += 1
                row_num += 1
            self._cables_crossing = int(variables_list[0][row_num - 1])
            previous_time = float(variables_list[1][row_num - 1])
            data.close()
            data = open(parameters["Log_file_name"][0], 'a')
        # Else initialize to 0
        else:
            self._cables_crossing = 0
            previous_time = 0.
            data = open(parameters["Log_file_name"][0], 'w')
            data.write("Cable Crossing,Time\n0,0\n")
            data.flush()

        time_init = time.time()

        while not self._stop.is_set():
            if gyro_x.value < \
                    float(parameters["Minimum_CableDetection"][0]) or \
                    gyro_x.value > \
                    float(parameters["Maximum_CableDetection"][0]) or\
                    gyro_y.value < \
                    float(parameters["Minimum_CableDetection"][0]) or \
                    gyro_y.value > \
                    float(parameters["Maximum_CableDetection"][0]):
                self._cables_crossing += 1
                data.write(str(self._cables_crossing) + "," +\
                        str(time.time() - time_init + previous_time) + "\n")
                print("\nnb of cables crossing: " + str(self._cables_crossing))
                data.flush()
                time.sleep(02)
            time.sleep(0.01)

    cables_crossing = property(_get_cables_crossing)


def robot_motion(config_test, motion):
    """
    Move function
    """
    list_velocity=[]
    time_test = float(config_test.get('config.cfg', 'Test_time'))
    robot_velocity_min = float(config_test.get('config.cfg', 'Robot_velocity_min'))
    robot_velocity_nom = float(config_test.get('config.cfg', 'Robot_velocity_nom'))
    robot_velocity_max = float(config_test.get('config.cfg', 'Robot_velocity_max'))
    list_velocity.append(robot_velocity_min)
    list_velocity.append(robot_velocity_nom)
    list_velocity.append(robot_velocity_max)

    for robot_velocity in list_velocity:
        motion.move(robot_velocity, 0, 0)
        time.sleep(time_test)
        motion.stopMove()


def record_inertialbase_data(
        get_all_inertialbase_objects, thread):
    """
    Function which logs the inertial base datas
    """
    logger = get_all_inertialbase_objects["logger"]
    coord = ["X", "Y", "Z"]
    t_0 = time.time()
    while thread.isAlive():
        for each in coord:
            logger.log(("Acc" + each, get_all_inertialbase_objects[
                "Acc" + each].value))
            logger.log(("Angle" + each, get_all_inertialbase_objects[
                "Angle" + each].value))
            logger.log(("Gyr" + each, get_all_inertialbase_objects[
                "Gyr" + each].value))
        logger.log(("Time", time.time() - t_0))
        time.sleep(0.005)
    return logger