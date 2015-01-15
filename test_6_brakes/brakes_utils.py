import math
import time
import logging

def are_joint_statics(wait_time, allowed_slip_angle, hippitch, kneepitch):
    """
    Return True if HipPitch and KneePitch joints did not slip more than an
    allowed slip angle for defined wait time.
    """
    initial_pos_hip = hippitch.position.sensor.value
    initial_pos_hip_degrees = math.degrees(initial_pos_hip)

    initial_pos_knee = kneepitch.position.sensor.value
    initial_pos_knee_degrees = math.degrees(initial_pos_knee)

    initial_time = time.time()

    state = True
    hip_static = True
    knee_static = True

    while ((time.time() - initial_time) <= wait_time) and state is True:
        pos_hip = hippitch.position.sensor.value
        pos_hip_degrees = math.degrees(pos_hip)

        pos_knee = kneepitch.position.sensor.value
        pos_knee_degrees = math.degrees(pos_knee)

        diff_hip_deg = abs(pos_hip_degrees - initial_pos_hip_degrees)
        if diff_hip_deg > allowed_slip_angle:
            logging.debug("hip static FALSE")
            hip_static = False

        diff_knee_deg = abs(pos_knee_degrees - initial_pos_knee_degrees)
        if diff_knee_deg > allowed_slip_angle:
            knee_static = False
            logging.debug("knee static FALSE")

        if (hip_static, knee_static) == (False, True):
            state = False
            logging.critical("Hip Slip")
        elif (hip_static, knee_static) == (True, False):
            state = False
            logging.critical("Knee Slip")
        elif (hip_static, knee_static) == (False, False):
            state = False
            logging.critical("Both Slip")

    return state

def print_joint_temperatures(hippitch, kneepitch):
    """print real joint temperatures."""
    logging.info(" ".join(["HipPitch Temperature =",
                           str(hippitch.temperature.value)]))
    logging.info(" ".join(["KneePitch Temperature =",
                           str(kneepitch.temperature.value)]))

