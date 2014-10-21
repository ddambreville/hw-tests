import qha_tools
import subdevice
import threading
import time
import os
import csv


class BumpersCounting(threading.Thread):
    """
    Class to check the number of bumper activations
    """
    def  __init__(self, dcm, mem, wait_time_bumpers):
        threading.Thread.__init__(self)
        self.dcm = dcm
        self.mem = mem
        self._bumpers_activations = 0
        self._is_bumper_pressed = False
        self._end_bumpers_activations = False
        self.wait_time_bumpers = wait_time_bumpers

    def _get_bumpers_activations(self):
        """
        To get the number of activations
        """
        return self._bumpers_activations

    def _get_is_bumper_pressed(self):
        """
        To know if a bumper is pressed
        """
        return self._is_bumper_pressed

    def run(self):
        bumper_right = subdevice.Bumper(self.dcm, self.mem, "FrontRight")
        bumper_left  = subdevice.Bumper(self.dcm, self.mem, "FrontLeft")
        bumper_back  = subdevice.Bumper(self.dcm, self.mem, "Back")

        list_bumpers = [bumper_right, bumper_left, bumper_back]

        parameters = qha_tools.read_section("config.cfg",
            "BumpersActivationsParameters")

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
        while not self._end_bumpers_activations:
            flag = 0
            self._is_bumper_pressed = False
            for bumper in list_bumpers:
                if bumper.value == 1:
                    flag += 1
                    self._bumpers_activations += 1
                    data.write(str(self._bumpers_activations) + "," + \
                               str(time.time() - time_init + previous_time) + "\n")
                    print("nb of bumpers activations: " + str(self._bumpers_activations))
                    data.flush()
            if flag > 0:
                self._is_bumper_pressed = True
            qha_tools.wait(self.dcm, self.wait_time_bumpers)
            # while bumper_right.value == 1 or \
            #       bumper_left.value == 1 or \
            #       bumper_back.value == 1:
            #     pass

    def stop(self):
        """
        To stop checking
        """
        self._end_bumpers_activations = True

    bumpers_activations = property(_get_bumpers_activations)
    is_bumper_pressed = property(_get_is_bumper_pressed)


class CablesCrossing(threading.Thread):
    """
    Class to check the number of cables crossing during a test
    """
    def __init__(self, dcm, mem):
        threading.Thread.__init__(self)
        self.dcm = dcm
        self.mem = mem
        self._cables_crossing = 0
        self._end_cables_crossing = False

    def _get_cables_crossing(self):
        """ To know the number of cables crossing """
        return self._cables_crossing

    def run(self):
        """Log cables crossing"""
        gyro_x = subdevice.InertialSensorBase(self.dcm, self.mem, "GyroscopeX")
        gyro_y = subdevice.InertialSensorBase(self.dcm, self.mem, "GyroscopeY")

        parameters = qha_tools.read_section("config.cfg", "CablesRoutingParameters")

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

        while not self._end_cables_crossing:
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
                print("nb of cables crossing: " + str(self._cables_crossing))
                data.flush()
            time.sleep(2)

    def stop(self):
        """ To stop checking """
        self._end_cables_crossing = True

    cables_crossing = property(_get_cables_crossing)
