import subdevice
import qha_tools


def fan_cycle(dcm, mem, nb_cycles, t_on=10000, t_off=10000):
    fan_hardness_actuator = subdevice.FanHardnessActuator(dcm, mem)
    for i in range(nb_cycles):
        fan_hardness_actuator.qqvalue = 1.0
        qha_tools.wait(dcm, t_on)
        fan_hardness_actuator.qqvalue = 0.0
        qha_tools.wait(dcm, t_off)
