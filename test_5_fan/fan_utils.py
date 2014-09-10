import subdevice
import tools


def fan_cycle(dcm, mem, nb_cycles, t_on=5000, t_off=5000):
    fan_hardness_actuator = subdevice.FanHardnessActuator(dcm, mem)
    for i in range(nb_cycles):
        fan_hardness_actuator.qqvalue = 1.0
        tools.wait(dcm, t_on)
        fan_hardness_actuator.qqvalue = 0.0
        tools.wait(dcm, t_off)
