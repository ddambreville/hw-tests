import pytest
import time
import subdevice
import tools
import threading
import os
import csv


class CablesCrossing(threading.Thread):
    """
    Class to check number of cables crossing during a test
    """
    def __init__(self, dcm, mem):
        threading.Thread.__init__(self)
        self.dcm = dcm
        self.mem = mem
        self._passage_de_cables = 0
        self._end_cables_crossing = False

    def _get_cables_crossing(self):
        """ To know the number of cables crossing """
        return self._passage_de_cables

    def run(self):
        """Log cables routing"""
        gyro_x = subdevice.InertialSensorBase(self.dcm, self.mem, "GyroscopeX")
        gyro_y = subdevice.InertialSensorBase(self.dcm, self.mem, "GyroscopeY")

        parameters = tools.read_section("test.cfg", "CablesRoutingParameters")

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
            self._passage_de_cables = int(variables_list[0][row_num - 1])
            precedent_time = float(variables_list[1][row_num - 1])
            data.close()
            data = open(parameters["Log_file_name"][0], 'a')

        # Else initialize to 0
        else:
            self._passage_de_cables = 0
            precedent_time = 0.

        time_init = time.time()
        # While non cable crossing for the first time, wait to create file
        while self._passage_de_cables == 0 and not self._end_cables_crossing:
            if gyro_x.value < float(parameters["Minimum"][0]) or \
                    gyro_x.value > float(parameters["Maximum"][0]) or\
                    gyro_y.value < float(parameters["Minimum"][0]) or \
                    gyro_y.value > float(parameters["Maximum"][0]):
                self._passage_de_cables = 1
                data = open(parameters["Log_file_name"][0], 'w')
                data.write("CablesCrossing,Time\n")
                data.write(str(self._passage_de_cables) + "," +\
                        str(time.time() - time_init + precedent_time) + "\n")
                data.flush()
                time.sleep(2)

        while not self._end_cables_crossing:
            if gyro_x.value < float(parameters["Minimum"][0]) or \
                    gyro_x.value > float(parameters["Maximum"][0]) or\
                    gyro_y.value < float(parameters["Minimum"][0]) or \
                    gyro_y.value > float(parameters["Maximum"][0]):
                self._passage_de_cables += 1
                data.write(str(self._passage_de_cables) + "," +\
                        str(time.time() - time_init + precedent_time) + "\n")
                data.flush()
                time.sleep(2)

        print("\n\nNumber cables crossing = " +\
               str(self._passage_de_cables) + "\n\n")

    def stop(self):
        """ To stop checking """
        self._end_cables_crossing = True

    cables_crossing = property(_get_cables_crossing)
