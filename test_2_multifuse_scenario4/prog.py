import naoqi
import subdevice
import math
import time
IP = "10.0.165.163"

try:
    motion = naoqi.ALProxy("ALMotion", IP, 9559)
    motion.exit()
except:
    print "motion killed"

dcm = naoqi.ALProxy("DCM", IP, 9559)
mem = naoqi.ALProxy("ALMemory", IP, 9559)

list_hardness = mem.getDataList("Hardness/Actuator/Value")
dcm.createAlias(["Hardness", list_hardness])

print list_hardness

dcm.set(["Hardness", "ClearAll", [[0., dcm.getTime(0)]]])

# joint_position_actuator = subdevice.JointPositionActuator(dcm, mem, "HeadPitch")
# joint_hardness_actuator = subdevice.JointHardnessActuator(dcm, mem, "HeadPitch")

# initial_max_pos = joint_position_actuator.value

# new_max = initial_max_pos + math.radians(5)

# joint_position_actuator.maximum = [[[new_max, dcm.getTime(0)]], "Merge"]

# joint_hardness_actuator.qqvalue = 1.

# joint_position_actuator.qvalue = (new_max, 5000)

# time.sleep(10)

# joint_hardness_actuator.qqvalue = 0.
