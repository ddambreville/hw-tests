import pytest
import subdevice
import time
import threading
import tools


@pytest.fixture(scope="session")
def cables_routing(request, dcm, mem):
    """
    Fixture which log number of cables routing
    """
    thread_flag = threading.Event()

    def log():
        """Log cables routing"""
        gyro_x = subdevice.InertialSensorBase(dcm, mem, "GyroscopeX")
        gyro_y = subdevice.InertialSensorBase(dcm, mem, "GyroscopeY")

        parameters = tools.read_section("test.cfg", "CablesRoutingParameters")

        passage_de_cables = 0
        data = open(parameters["Log_file_name"][0], 'w')
        data.write("CablesRouting,Time\n")

        time_init = time.time()
        while not thread_flag.is_set() and \
                passage_de_cables < int(parameters["Nb_cables_routing"][0]):
            if gyro_x.value < float(parameters["Minimum"][0]) or \
                    gyro_x.value > float(parameters["Maximum"][0]) or\
                    gyro_y.value < float(parameters["Minimum"][0]) or \
                    gyro_y.value > float(parameters["Maximum"][0]):
                passage_de_cables += 1
                data.write(str(passage_de_cables) + "," +\
                        str(time.time() - time_init) + "\n")
                data.flush()
                time.sleep(2)

        print("\n\nNumber cables routing = " + str(passage_de_cables) +"\n\n")

    my_thread = threading.Thread(target=log)
    my_thread.start()

    def fin():
        """Stop logging"""
        thread_flag.set()

    request.addfinalizer(fin)
