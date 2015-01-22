import subdevice
import qha_tools

PROTECTION = 0.5

def head_behavior(dcm, mem, ctime, head_behavior_number):
    """Head behavior for false positive test."""

    head_pitch = subdevice.Joint(dcm, mem, "HeadPitch")
    head_yaw = subdevice.Joint(dcm, mem, "HeadYaw")

    headpitch_pos_max = PROTECTION * head_pitch.position.actuator.maximum
    headpitch_pos_min = PROTECTION * head_pitch.position.actuator.minimum

    headyaw_pos_max = PROTECTION * head_yaw.position.actuator.maximum
    headyaw_pos_min = PROTECTION * head_yaw.position.actuator.minimum

    for _ in range(head_behavior_number):
        head_pitch.position.actuator.qvalue = (headpitch_pos_max, ctime)
        head_yaw.position.actuator.qvalue = (headyaw_pos_max, ctime)
        qha_tools.wait(dcm, ctime)

        head_pitch.position.actuator.qvalue = (0.0, ctime / 2.)
        head_yaw.position.actuator.qvalue = (0.0, ctime / 2.)
        qha_tools.wait(dcm, ctime)

        head_pitch.position.actuator.qvalue = (headpitch_pos_min, ctime)
        head_yaw.position.actuator.qvalue = (headyaw_pos_min, ctime)
        qha_tools.wait(dcm, ctime)

        head_pitch.position.actuator.qvalue = (0.0, ctime / 2.)
        head_yaw.position.actuator.qvalue = (0.0, ctime / 2.)
        qha_tools.wait(dcm, ctime)

        head_pitch.position.actuator.qvalue = (headpitch_pos_max, ctime)
        head_yaw.position.actuator.qvalue = (headyaw_pos_min, ctime)
        qha_tools.wait(dcm, ctime)

        head_pitch.position.actuator.qvalue = (0.0, ctime / 2.)
        head_yaw.position.actuator.qvalue = (0.0, ctime / 2.)
        qha_tools.wait(dcm, ctime)

        head_pitch.position.actuator.qvalue = (headpitch_pos_min, ctime)
        head_yaw.position.actuator.qvalue = (headyaw_pos_max, ctime)
        qha_tools.wait(dcm, ctime)

        head_pitch.position.actuator.qvalue = (0.0, ctime / 2.)
        head_yaw.position.actuator.qvalue = (0.0, ctime / 2.)
        qha_tools.wait(dcm, ctime)



