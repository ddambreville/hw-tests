import subdevice
import math
import time
import brakes_utils
import logging
import numpy


def test_holding_cone(kill_motion, dcm, mem, stiffness_on, wake_up_pos, rest_pos,
    hc_joint, hc_direction, initial_angle, step, allowed_slip_number,
    allowed_slip_angle, wait_time, holding_cone, hippitch, kneepitch,
    dico_results, print_results, initialize_logger, wait_between_two_tests):

    # Test informations
    logging.info("")
    logging.info("*********************************")
    logging.info(" ".join(["TESTING", hc_joint.upper(), hc_direction.upper()]))
    logging.info("*********************************")
    logging.info("")

    # stiff robot and put it to wakeUp position
    subdevice.multiple_set(dcm, mem, stiffness_on, wait=True)
    subdevice.multiple_set(dcm, mem, wake_up_pos, wait=True)

    hip_mechstop_deg = abs(math.degrees(hippitch.position.actuator.maximum))
    knee_mechstop_deg = abs(math.degrees(kneepitch.position.actuator.maximum))

    initial_command = float(initial_angle[hc_joint][hc_direction])

    hippitch_max_temperature = hippitch.temperature.maximum - 10.0
    kneepitch_max_temperature = kneepitch.temperature.maximum - 10.0

    flag_close_to_mechstop = False
    flag_close_one_brake = False
    flag_anormal_state = False
    flag_hot_joint = False
    cpt_slip = 0

    while cpt_slip < allowed_slip_number and \
    flag_close_to_mechstop is False and \
    flag_hot_joint is False:
        try:
            logging.info(" ".join([hc_joint,
                                   hc_direction,
                                   str(initial_command),
                                   "deg"]))

            #opening brakes
            (hippitch.hardness.qqvalue, kneepitch.hardness.qqvalue) = (1.0, 1.0)

            # setting joint positions
            if hc_joint == "HipPitch":
                hippitch.position.actuator.qvalue = \
                (math.radians(initial_command), 3000)
                kneepitch.position.actuator.qvalue = (0.0, 3000)
            else:
                kneepitch.position.actuator.qvalue = \
                (math.radians(initial_command), 3000)
                hippitch.position.actuator.qvalue = (0.0, 3000)
            #waiting one more second to wait for stabilization
            time.sleep(4.0)

            # closing brakes
            if flag_close_one_brake is False:
                (hippitch.hardness.qqvalue, kneepitch.hardness.qqvalue) = \
                (0.0, 0.0)
            elif hc_joint == "HipPitch":
                (hippitch.hardness.qqvalue, kneepitch.hardness.qqvalue) = \
                (0.0, 1.0)
                logging.debug("closing only Hip brake")
            elif hc_joint == "KneePitch":
                (hippitch.hardness.qqvalue, kneepitch.hardness.qqvalue) = \
                (1.0, 0.0)
                logging.debug("closing only Knee brake")

            time.sleep(0.1)

            if hc_joint == "HipPitch":
                real_angle = hippitch.position.sensor.value
                real_angle_degrees = math.degrees(real_angle)
            else:
                real_angle = kneepitch.position.sensor.value
                real_angle_degrees = math.degrees(real_angle)

            # print real informations
            logging.info(" ".join([
                "Real joint angle =",
                str(round(real_angle_degrees, 2)),
                "deg"
                ]))

            state = brakes_utils.are_joint_statics(wait_time,
                                                   allowed_slip_angle,
                                                   hippitch, kneepitch)

            logging.debug(" state : " + str(state))

            brakes_utils.print_joint_temperatures(hippitch, kneepitch)

            if hc_joint == "HipPitch" and state == (True, False):
                flag_anormal_state = True
                logging.debug("Set flag anormal state to True")
            elif hc_joint == "KneePitch" and state == (False, True):
                flag_anormal_state = True
                logging.debug("Set flag anormal state to True")
            else:
                flag_anormal_state = False

            if flag_anormal_state and not flag_close_one_brake:
                flag_close_one_brake = True
                logging.debug("Set flag close one brake to True")
                logging.warning("**!! Incoherent state, Other joint slip !!**")
                logging.info("From now, other joint will stay stiffed")
                flag_anormal_state = False
                logging.debug("Set flag anormal state to False")

            if state == (True, True):
                logging.info("SUCCESS")
                if hc_direction == "Positive":
                    logging.debug("decrementing position")
                    initial_command -= step[hc_joint]
                else:
                    logging.debug("incrementing position")
                    initial_command += step[hc_joint]
            else:
                (hippitch.hardness.qqvalue, kneepitch.hardness.qqvalue) = \
                (1.0, 1.0)
                if hc_direction == "Negative":
                    initial_command -= 3
                else:
                    initial_command += 3
                if flag_anormal_state is False:
                    cpt_slip += 1
                    logging.debug("Incrementing slip counter")
                    list_results = dico_results[hc_joint][hc_direction]
                    if hc_joint == "HipPitch":
                        joint_temperature = hippitch.temperature.value
                    else:
                        joint_temperature = kneepitch.temperature.value
                    tuple_result = \
                    (round(real_angle_degrees, 2), joint_temperature)
                    list_results.append(tuple_result)

            # making sure mechanical stop is not going to be reached
            if hc_joint == "HipPitch" and\
             abs(initial_command) >\
              hip_mechstop_deg - 5.0:
                flag_close_to_mechstop = True
                logging.info("Too close to mechanical stop")
            elif hc_joint == "KneePitch" and\
             abs(initial_command) >\
              knee_mechstop_deg - 5.0:
                flag_close_to_mechstop = True
                logging.info("Too close to mechanical stop")

            # making sure that joints are not too hot
            if hippitch.temperature.value > hippitch_max_temperature:
                flag_hot_joint = True
                logging.warning("HipPitch Temperature too high to continue")

            if kneepitch.temperature.value > kneepitch_max_temperature:
                flag_hot_joint = True
                logging.warning("KneePitch Temperature too high to continue")

        except KeyboardInterrupt:
            (hippitch.hardness.qqvalue, kneepitch.hardness.qqvalue) = \
            (1.0, 1.0)
            logging.warning("!!! Test stopped by user !!! (KeyboardInterrupt")
            subdevice.multiple_set(dcm, mem, rest_pos, wait=True)
            break

    logging.debug(str(dico_results))
    # assertion
    try:
        result_list_brut = dico_results[hc_joint][hc_direction]
        result_list = [list(x) for x in zip(*result_list_brut)]
        angle_list = result_list[0]
        min_value = numpy.amin(numpy.absolute(angle_list))
        assert min_value >= abs(holding_cone[hc_joint][hc_direction])
    except:
        assert None


def test_cycling(motion, cycle_number):
    """Brakes cycling test."""
    #logger init
    log = logging.getLogger('test_cycling')
    i = 0
    while i < cycle_number:
        try:
            log.info("cycle number : " + str(i+1))
            motion.wakeUp()
            if motion.robotIsWakeUp() is True:
                motion.setMotionConfig([["ENABLE_BRAKES_PROTECTION", False]])
                motion.rest()
                motion.setMotionConfig([["ENABLE_BRAKES_PROTECTION", True]])
                i += 1
            else:
                log.warning("robot did not wake up !!!!!")
            time.sleep(5)
        except KeyboardInterrupt:
            log.warning("cycling interrupted by user")
            motion.rest()
            break
