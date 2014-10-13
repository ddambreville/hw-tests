'''
Created on October 13, 2014

@author: amartin
'''

import time
import easy_plot_connection


def display_inertialbase_data(
        inertialbase_objects_rt):
    """
    Function which displays the inertial base datas
    """
    coord = ["X", "Y", "Z"]
    plot_server = easy_plot_connection.Server(local_plot=True, max_points=100)
    t_0 = time.time()
    display = True
    while display:
        try:
            for each in coord:
                elapsed_time = time.time() - t_0
                plot_server.add_point("Acc" + each, elapsed_time, \
                    inertialbase_objects_rt["Acc" + each].value)
                plot_server.add_point("Angle" + each, elapsed_time, \
                    inertialbase_objects_rt["Angle" + each].value)
                plot_server.add_point("Gyr" + each, elapsed_time, \
                    inertialbase_objects_rt["Gyr" + each].value)
            time.sleep(0.005)
        except KeyboardInterrupt:
            print "\r"
            display = False

