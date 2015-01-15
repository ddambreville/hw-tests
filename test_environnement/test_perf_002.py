import pytest
import qha_tools
import subdevice
import time
import uuid
import multi_logger


class EventModule(object):

    """
    Module which launch function if event detected.
    """

    def __init__(self, mem):
        """
        @mem        : proxy to ALMemory (object)
        """
        self.mem = mem
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
            self.mem.subscribeToEvent(k, module_name, "_event_detected")

    def _event_detected(self):
        """
        Function triggered when event is detected.
        Change flags.
        """
        event_detected = str(self.mem.getData("FaceDetected"))
        if event_detected == "[]":
            print "False"
            self._flag_event = 0
        else:
            print "True"
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



def test_face_detection(robot_ip, dcm, mem, motion, session,
                         motion_wake_up, parameters):
    """
    Docstring
    """
    expected = {"FaceDetected": 1}
    module_name = "EventChecker_{}_".format(uuid.uuid4())
    face_detected = EventModule(mem)
    module_id = session.registerService(module_name, face_detected)
    face_detected.subscribe(module_name, expected)

    flag_end_face = False
    flag_face = False

    log = multi_logger.Logger(
        robot_ip,
        "multi_logger.cfg",
        0.1,
        parameters["FileName"][0]
    )
    log.log()

    while not flag_end_face:
        try:
            if face_detected.flag_event:
                flag_face = True
            if flag_face and not face_detected.flag_event:
                flag_end_face = True
        except KeyboardInterrupt:
            break

    log.stop()

    session.unregisterService(module_id)

    assert face_detected.flag