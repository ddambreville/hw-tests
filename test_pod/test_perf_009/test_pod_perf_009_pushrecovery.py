import pytest
import time
import threading
import uuid
import qha_tools
import log_pod


class EventModule(object):

    """
    Module which launch function if event detected.
    """

    def __init__(self, mem, event):
        """
        @mem        : proxy to ALMemory (object)
        @event      : ALMemory key of the event expected (string)
        """
        self._mem = mem
        self._event_name = event
        self._flag_event = 0      # = 1 when event detected, else = 0
        self._flag = False        # True when event detected at least one time

    def subscribe(self, module_name, events):
        """
        Subscribe to event.
        Run function when event is detected.

        @module_name    : event module name
        @ events        : events expected (dictionnary)
        """
        for k in events.keys():
            self._mem.subscribeToEvent(k, module_name, "_event_detected")

    def _event_detected(self):
        """
        Function triggered when event is detected.
        Change flags.
        """
        event_detected = str(self._mem.getData(self._event_name))
        print("Event detected : " + event_detected)
        self._flag_event = 1
        self._flag = True

    def _get_flag_event(self):
        """
        Return flag event.
        """
        return self._flag_event

    def _get_flag(self):
        """
        Return flag.
        """
        return self._flag

    flag_event = property(_get_flag_event)
    flag = property(_get_flag)


def test_pod_pushrecovery(dcm, mem, alleds, session, motion_wake_up,
                          parameters):
    """
    Test pod during wakeUp : no base mouvement.
    Assert True is no fall down detected.

    @dcm            : proxt to DCM (object)
    @mem            : proxy to ALMemory (object)
    @alleds         : proxy to ALLeds (object)
    @session        : Session in qi (object)
    @motion_wake_up : robot does his wakeUp
    @parameters     : dictionnary {"parameter":value} from config file
                      (dictionnary)
    """

    # Subcribe to module
    expected = {"ALMotion/Safety/PushRecovery": 1}
    module_name = "EventChecker_{}_".format(uuid.uuid4())
    push_recovery = EventModule(mem, "ALMotion/Safety/PushRecovery")
    module_id = session.registerService(module_name, push_recovery)
    push_recovery.subscribe(module_name, expected)

    log = log_pod.Log(dcm, mem, push_recovery, parameters["PRFileName"][0])
    log.start()

    alleds.fadeRGB("FaceLeds", "blue", 0)

    time.sleep(int(parameters["TimeWait"][0]))

    log.stop()

    alleds.fadeRGB("FaceLeds", "white", 0)

    session.unregisterService(module_id)

    if push_recovery.flag:
        assert True
    else:
        assert False
