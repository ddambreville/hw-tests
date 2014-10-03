import pytest
import subdevice
import time
import threading
import tools
import os
import csv


@pytest.fixture(scope="session")
def cables_routing(request, dcm, mem, rest_pos):
    """
    Fixture which log number of cables routing
    """
    thread_flag = threading.Event()

    def log():
        """Log cables routing"""
        gyro_x = subdevice.InertialSensorBase(dcm, mem, "GyroscopeX")
        gyro_y = subdevice.InertialSensorBase(dcm, mem, "GyroscopeY")

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
            passage_de_cables = int(variables_list[0][row_num - 1])
            precedent_time = float(variables_list[1][row_num - 1])
            data.close()
            data = open(parameters["Log_file_name"][0], 'a')

        else:
            data = open(parameters["Log_file_name"][0], 'w')
            data.write("CablesRouting,Time\n")
            passage_de_cables = 0
            precedent_time = 0.

        time_init = time.time()
        while not thread_flag.is_set():
            if gyro_x.value < float(parameters["Minimum"][0]) or \
                    gyro_x.value > float(parameters["Maximum"][0]) or\
                    gyro_y.value < float(parameters["Minimum"][0]) or \
                    gyro_y.value > float(parameters["Maximum"][0]):
                passage_de_cables += 1
                data.write(str(passage_de_cables) + "," +\
                        str(time.time() - time_init + precedent_time) + "\n")
                data.flush()
                time.sleep(2)

        print("\n\nNumber cables routing = " + str(passage_de_cables) +"\n\n")

    my_thread = threading.Thread(target=log)
    my_thread.start()

    def fin():
        """Stop logging"""
        thread_flag.set()

    request.addfinalizer(fin)
