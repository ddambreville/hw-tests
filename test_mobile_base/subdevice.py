'''
Created on May 17, 2013

@author: enalepa

Updated by tcharles on August 2014:
The following classes have been added
- JointHardnessActuator
- MultiFuseBoardAmbiantTemperature
- MultiFuseBoardTotalCurrent
- FuseTemperature
- FuseCurrent
- FuseVoltage
- FanHardnessActuator
- FanFrequencySensor
- FanStatus
'''

import tools
from math import pi, cos


def multiple_set(dcm, mem, datas, update_type="ClearAll", wait=False):
    """
    Allows robot to take the chosen position.
    Robot must be stiffed before.
    """
    times = [int(time) for time in datas["Time"]]
    datas_without_time = datas.copy()
    datas_without_time.pop("Time")

    dcm.createAlias(
        [
            "Alias",
            [item + "/Value" for item in datas_without_time.keys()]
        ]
    )

    for name, command in datas_without_time.items():
        for index, value in enumerate(command):
            if value == "min":
                sub = SubDevice(dcm, mem, name)
                command[index] = sub.minimum
            elif value == "max":
                sub = SubDevice(dcm, mem, name)
                command[index] = sub.maximum
            else:
                command[index] = float(value)

    dcm.setAlias(
        [
            "Alias",
            update_type,
            "time-separate",
            0,
            [dcm.getTime(time) for time in times],
            datas_without_time.values()
        ]
    )

    if wait:
        tools.wait(dcm, times[-1])


class SubDevice(object):

    """Class which describes a joint."""

    def __init__(self, dcm, mem, name):
        self.dcm = dcm
        self.mem = mem
        self.name = name

        self.prefix = self.dcm.getPrefix()[0]

    def _get_device(self):
        """Get subdevice's device from ALMemory."""
        return self.get("Device")

    def _set_device(self, request):
        """Set subdevice's device"""
        self.set("Device", request[0], request[1])

    def _get_gain(self):
        """Get subdevice's gain."""
        return self.get("Gain")

    def _set_gain(self, request):
        """Set subdevice's gain."""
        self.set("Gain", request[0], request[1])

    def _get_maximum(self):
        """Get subdevice's max value."""
        return self.get("Max")

    def _set_maximum(self, request):
        """Set subdevice's max value."""
        self.set("Max", request[0], request[1])

    def _get_minimum(self):
        """Get subdevice's min value."""
        return self.get("Min")

    def _set_minimum(self, request):
        """Set subdevice's min value."""
        self.set("Min", request[0], request[1])

    def _get_offset(self):
        """Get subdevice's offset value."""
        return self.get("Offset")

    def _set_offset(self, request):
        """Set subdevice's offset value."""
        self.set("Offset", request[0], request[1])

    def _get_register(self):
        """Get subdevice's register."""
        return self.get("Register")

    def _set_register(self, request):
        """Set subdevice's register."""
        self.set("Register", request[0], request[1])

    def _get_subdevice_number(self):
        """Get subdevice's number."""
        return self.get("SubDeviceNumber")

    def _set_subdevice_number(self, request):
        """Set subdevice's number."""
        self.set("SubDeviceNumber", request[0], request[1])

    def _get_subdevice_type(self):
        """Get subdevice's type."""
        return self.get("Type")

    def _set_subdevice_type(self, request):
        """Set subdevice's type."""
        self.set("Type", request[0], request[1])

    def _get_value(self):
        """Get subdevice's value."""
        return self.get("Value")

    def _set_value(self, request):
        """Set subdevice's value."""
        self.set("Value", request[0], request[1])

    def _get_quick_value(self):
        """Get subdevice's value."""
        return self.get("Value")

    def _set_quick_value(self, valeur):
        """Set subdevice's value."""
        self.set("Value", [[valeur[0], self.dcm.getTime(valeur[1])]])

    def _get_quick_quick_value(self):
        """Get subdevice's value."""
        return self.get("Value")

    def _set_quick_quick_value(self, valeur):
        """Set subdevice's value immediatly to the chosen value 'valeur'."""
        if self.subdevice_type not in ("ActuatorJointSpeed", "Joint"):
            self.set("Value", [[valeur, self.dcm.getTime(0)]])
        else:
            print "qqvalue does not work with joints position actuator"
            print "qqvalue does not work with wheels speed actuator"

    def _get_multiple_quick_value(self):
        """Get subdevice's value."""
        return self.get("Value")

    def _set_multiple_quick_value(self, list_of_tuples):
        """
        Set subdevice's value.
        joint_hard_act = subdevice.JointHardnessActuator(dcm, mem, "HipPitch")
        joint_hard_act.mqvalue = [(1, 0), (1, 1000), (0, 1001)]
        """
        list_of_tuples = \
            [[float(tup[0]), self.dcm.getTime(tup[1])]
             for tup in list_of_tuples]
        self.set("Value", list_of_tuples)

    device = property(_get_device, _set_device)
    gain = property(_get_gain, _set_gain)
    maximum = property(_get_maximum, _set_maximum)
    minimum = property(_get_minimum, _set_minimum)
    offset = property(_get_offset, _set_offset)
    register = property(_get_register, _set_register)
    subdevice_number = property(_get_subdevice_number, _set_subdevice_number)
    subdevice_type = property(_get_subdevice_type, _set_subdevice_type)
    value = property(_get_value, _set_value)
    qvalue = property(_get_quick_value, _set_quick_value)
    qqvalue = property(_get_quick_quick_value, _set_quick_quick_value)
    mqvalue = property(_get_multiple_quick_value, _set_multiple_quick_value)

    def get(self, attribut):
        """Accessor which uses ALMemory module."""
        return self.mem.getData(self.prefix + self.name + "/" + attribut)

    def set(self, attribut, timed_commands, update_type="ClearAll"):
        """Mutator which uses DCM module."""
        key = self.name + "/" + attribut
        self.dcm.set([key, update_type, timed_commands])


class JointPositionActuator(SubDevice):

    """
    Class which defines a joint characterized by :
    - its sub-device
    - its maximum current
    - its invert direction control
    - its gain coefficient
    - its integrator coefficient
    - its derivator coefficient
    - its motor number
    - its pulse width modulation value
    """

    def __init__(self, dcm, mem, short_name):
        SubDevice.__init__(self, dcm, mem, short_name)
        self.short_name = short_name
        self.header_name = "_".join([self.short_name, "Position", "Actuator"])
        self.name = short_name + "/Position/Actuator"

    def _get_max_current(self):
        """Get joint's max allowed current."""
        return self.get("IMax")

    def _set_max_current(self, request):
        """Set joint's max allowed current."""
        self.set("IMax", request[0], request[1])

    def _get_invert_control_direction(self):
        """Get invert control direction."""
        return self.get("InvertControlDirection")

    def _set_invert_control_direction(self, request):
        """Set invert control direction."""
        self.set("InvertControlDirection", request[0], request[1])

    def _get_k_d(self):
        """Get derivative coefficient of PID corrector."""
        return self.get("Kd")

    def _set_k_d(self, request):
        """Set derivative coefficient of PID corrector."""
        self.set("Kd", request[0], request[1])

    def _get_k_i(self):
        """Get integral coefficient of PID corrector."""
        return self.get("Ki")

    def _set_k_i(self, request):
        """Get integral coefficient of PID corrector."""
        self.set("Kd", request[0], request[1])

    def _get_k_p(self):
        """Get proportionnal coefficient of PID corrector."""
        return self.get("Kp")

    def _set_k_p(self, request):
        """Set proportionnal coefficient of PID corrector."""
        self.set("Kd", request[0], request[1])

    def _get_motor_number(self):
        """Get joint's motor number."""
        return self.get("MotorNumber")

    def _set_motor_number(self, request):
        """Set joint's motor number."""
        self.set("MotorNumber", request[0], request[1])

    def _get_pwm_value(self):
        """Get joint motor PWM value."""
        return self.get("PWMValue")

    def _set_pwm_value(self, request):
        """Set joint motor PWM value."""
        self.set("PWMValue", request[0], request[1])

    max_current = property(_get_max_current, _set_max_current)
    invert_control_direction = property(
        _get_invert_control_direction,
        _set_invert_control_direction
    )
    k_d = property(_get_k_d, _set_k_d)
    k_i = property(_get_k_i, _set_k_i)
    k_p = property(_get_k_p, _set_k_p)
    motor_number = property(_get_motor_number, _set_motor_number)
    pwm_value = property(_get_pwm_value, _set_pwm_value)

    def go_to(self, dcm, position, time=3000., update_type="ClearAll", wait=True):
        """To comment."""
        if position == "min":
            position = self.minimum
        elif position == "max":
            position = self.maximum
        else:
            position = float(position)

        self.value = [[[position, self.dcm.getTime(time)]], update_type]

        if wait:
            tools.wait(dcm, time)

    def explore(self, time_to_go_limit, max_to_min=True):
        """
        The chosen joint is goint to explore the two mechanical stops.
        - First: goes to its max position in 'time_to_go_limit' seconds.
        - Then: goes to its min position in 'time_to_go_limit' seconds.
        Non blocking method.
        """
        if max_to_min:
            self.dcm.set(
                [
                    self.name + "/Value",
                    "ClearAll",
                    [
                        [self.maximum, self.dcm.getTime(time_to_go_limit)],
                        [self.minimum, self.dcm.getTime(2 * time_to_go_limit)]
                    ]
                ])
        else:
            self.dcm.set(
                [
                    self.name + "/Value",
                    "ClearAll",
                    [
                        [self.minimum, self.dcm.getTime(time_to_go_limit)],
                        [self.maximum, self.dcm.getTime(2 * time_to_go_limit)]
                    ]
                ])


class JointPositionSensor(SubDevice):

    """
    Class which defines a joint characterized by :
    - its gear ratio
    - its limit sensor position
    - its max mechanical stop
    - its min mechanical stop
    - its sensor type
    - its zero position
    - its position chain MRE joint
    - its position chain MRE motor
    """

    def __init__(self, dcm, mem, short_name):
        SubDevice.__init__(self, dcm, mem, short_name)
        self.short_name = short_name
        self.header_name = "_".join([self.short_name, "Position", "Sensor"])
        self.name = short_name + "/Position/Sensor"

    def _get_gear_ratio(self):
        """Get geat ratio."""
        return self.get("GearRatio")

    def _set_gear_ratio(self, request):
        """Set geat ratio."""
        self.set("GearRatio", request[0], request[1])

    def _get_limit(self):
        """Get position sensor limit."""
        return self.get("Limit")

    def _set_limit(self, request):
        """Set position sensor limit."""
        self.set("Limit", request[0], request[1])

    def _get_mechanical_stop_max(self):
        """Get max mechanical stop."""
        return self.get("MechanicalStopMax")

    def _set_mechanical_stop_max(self, request):
        """Set max mechanical stop."""
        self.set("MechanicalStopMax", request[0], request[1])

    def _get_mechanical_stop_min(self):
        """Get mix mechanical stop."""
        return self.get("MechanicalStopMin")

    def _set_mechanical_stop_min(self, request):
        """Set mix mechanical stop."""
        self.set("MechanicalStopMin", request[0], request[1])

    def _get_sensor_type(self):
        """Get sensor type."""
        return self.get("SensorType")

    def _set_sensor_type(self, request):
        """Set sensor type."""
        self.set("SensorType", request[0], request[1])

    def _get_joint_zero_position(self):
        """Get joint zero position."""
        return self.get("jointZeroPosition")

    def _set_joint_zero_position(self, request):
        """Set joint zero position."""
        self.set("jointZeroPosition", request[0], request[1])

    def _get_position_chain_mre_joint(self):
        """Get position chain MRE joint."""
        return self.get("positionChainMREJoint")

    def _set_position_chain_mre_joint(self, request):
        """Set position chain MRE joint."""
        self.set("positionChainMREJoint", request[0], request[1])

    def _get_position_chain_mre_motor(self):
        """Get position chain MRE motor."""
        return self.get("positionChainMREMotor")

    def _set_position_chain_mre_motor(self, request):
        """Set position chain MRE motor."""
        self.set("positionChainMREMotor", request[0], request[1])

    gear_ratio = property(_get_gear_ratio, _set_gear_ratio)
    limit = property(_get_limit, _set_limit)
    mechanical_stop_max = property(
        _get_mechanical_stop_max,
        _set_mechanical_stop_max)
    mechanical_stop_min = property(
        _get_mechanical_stop_min,
        _set_mechanical_stop_min)
    sensor_type = property(_get_sensor_type, _set_sensor_type)
    joint_zero_position = property(
        _get_joint_zero_position,
        _set_joint_zero_position)
    position_chain_mre_joint = property(
        _get_position_chain_mre_joint,
        _set_position_chain_mre_joint)
    position_chain_mre_motor = property(
        _get_position_chain_mre_motor,
        _set_position_chain_mre_motor)


class JointHardnessActuator(SubDevice):

    """
    Class which defines a joint hardness characterized by :
    - its stiffness decrease rate
    """

    def __init__(self, dcm, mem, short_name):
        SubDevice.__init__(self, dcm, mem, short_name)
        self.short_name = short_name
        self.header_name = "_".join([self.short_name, "Actuator"])
        self.name = short_name + "/Hardness/Actuator"

    def _get_stiffness_decrease_rate(self):
        """Get stiffness decrease rate."""
        return self.get("stiffnessDecreaseRate")

    def _set_stiffness_decrease_rate(self, request):
        """Get stiffness decrease rate."""
        self.set("stiffnessDecreaseRate", request[0], request[1])

    stiffness_decrease_rate = property(
        _get_stiffness_decrease_rate,
        _set_stiffness_decrease_rate)


class JointCurrentSensor(SubDevice):

    """
    Class which defines a joint characterized by :
    - its current type
    - its shunt resistance
    """

    def __init__(self, dcm, mem, short_name):
        SubDevice.__init__(self, dcm, mem, short_name)
        self.short_name = short_name
        self.header_name = "_".join([self.short_name, "Current"])
        self.name = short_name + "/ElectricCurrent/Sensor"

    def _get_current_type(self):
        """Get current type."""
        return self.get("CurrentType")

    def _set_current_type(self, request):
        """Set current type."""
        self.set("CurrentType", request[0], request[1])

    def _get_shunt_resistance(self):
        """Get shunt resistance value."""
        return self.get("ShuntResistance")

    def _set_shunt_resistance(self, request):
        """Set shunt resistance value."""
        self.set("ShuntResistance", request[0], request[1])

    current_type = property(_get_current_type, _set_current_type)
    shunt_resistance = property(_get_shunt_resistance, _set_shunt_resistance)


class JointTemperature(SubDevice):

    """
    Class which defines a joint characterized by :
    - its adress temperature sensor
    - its other motor other motor transmission
    - its start temperature
    - its temperature sensor type
    - its thermal resistance
    - its motor model
    - its ambiant temperature
    """

    def __init__(self, dcm, mem, short_name):
        SubDevice.__init__(self, dcm, mem, short_name)
        self.short_name = short_name
        self.header_name = "_".join([self.short_name, "Temperature"])
        self.name = short_name + "/Temperature/Sensor"

    def _get_adress_temperature_sensor(self):
        """Get adress temperature sensor."""
        return self.get("AdressTemperatureSensor")

    def _set_adress_temperature_sensor(self, request):
        """Set adress temperature sensor."""
        self.set("AdressTemperatureSensor", request[0], request[1])

    def _get_other_motor_transmission(self):
        """Get other motor transmission."""
        return self.get("OtherMotorTransmission")

    def _set_other_motor_transmission(self, request):
        """Set other motor transmission."""
        self.set("OtherMotorTransmission", request[0], request[1])

    def _get_start_temperature(self):
        """Get start temperature."""
        return self.get("StartTemperature")

    def _set_start_temperature(self, request):
        """Set start temperature."""
        self.set("StartTemperature", request[0], request[1])

    def _get_temperature_sensor_type(self):
        """Get temperature sensor type."""
        return self.get("TemperatureSensorType")

    def _set_temperature_sensor_type(self, request):
        """Set temperature sensor type."""
        self.set("TemperatureSensorType", request[0], request[1])

    def _get_thermal_resistance(self):
        """Get thermal resistance."""
        return self.get("ThermalResistance")

    def _set_thermal_resistance(self, request):
        """Set thermal resistance."""
        self.set("ThermalResistance", request[0], request[1])

    def _get_motor_model(self):
        """Get motor_model."""
        return self.get("motorModel")

    def _set_motor_model(self, request):
        """Set motor_model."""
        self.set("motorModel", request[0], request[1])

    def _get_ambiant_temperature(self):
        """Get ambiant temperature."""
        return self.get("AmbiantTemperature")

    def _set_ambiant_temperature(self, request):
        """Set ambiant temperature."""
        self.set("AmbiantTemperature", request[0], request[1])

    def _get_status(self):
        """Get subdevice status."""
        return self.get("Status")

    def _set_status(self, request):
        """Set subdevice status."""
        self.set("Status", request[0], request[1])

    def _get_thermal_time_constant(self):
        """Get thermal time constant."""
        return self.get("ThermalTimeConstant")

    def _set_thermal_time_constant(self, request):
        """Set thermal time constant."""
        self.set("ThermalTimeConstant", request[0], request[1])

    def _get_winding_resistance(self):
        """Get winding resistance."""
        return self.get("WindingResistance")

    def _set_winding_resistance(self, request):
        """Set winding resistance."""
        self.set("WindingResistance", request[0], request[1])

    adress_temperature_sensor = property(
        _get_adress_temperature_sensor,
        _set_adress_temperature_sensor)
    other_motor_transmission = property(
        _get_other_motor_transmission,
        _set_other_motor_transmission)
    start_temperature = property(
        _get_start_temperature,
        _set_start_temperature)
    temperature_sensor_type = property(
        _get_temperature_sensor_type,
        _set_temperature_sensor_type)
    thermal_resistance = property(
        _get_thermal_resistance,
        _set_thermal_resistance)
    motor_model = property(_get_motor_model, _set_motor_model)
    ambiant_temperature = property(
        _get_ambiant_temperature,
        _set_ambiant_temperature)
    status = property(_get_status, _set_status)
    thermal_time_constant = property(
        _get_thermal_time_constant,
        _set_thermal_time_constant)
    winding_resistance = property(
        _get_winding_resistance,
        _set_winding_resistance)

# Wheels classes


class WheelSpeedActuator(SubDevice):

    """
    Describes wheels speed actuator.
    ShortName can be in ["WheelFR","WheelFL","WheelB"].
    """

    def __init__(self, dcm, mem, short_name):
        SubDevice.__init__(self, dcm, mem, short_name)
        self.short_name = short_name
        self.name = short_name + "/Speed/Actuator"

    def _get_max_current(self):
        """Get joint's max allowed current."""
        return self.get("IMax")

    def _set_max_current(self, request):
        """Set joint's max allowed current."""
        self.set("IMax", request[0], request[1])

    def _get_invert_control_direction(self):
        """Get invert control direction."""
        return self.get("InvertControlDirection")

    def _set_invert_control_direction(self, request):
        """Set invert control direction."""
        self.set("InvertControlDirection", request[0], request[1])

    def _get_k_d(self):
        """Get derivative coefficient of PID corrector."""
        return self.get("Kd")

    def _set_k_d(self, request):
        """Set derivative coefficient of PID corrector."""
        self.set("Kd", request[0], request[1])

    def _get_k_i(self):
        """Get integral coefficient of PID corrector."""
        return self.get("Ki")

    def _set_k_i(self, request):
        """Get integral coefficient of PID corrector."""
        self.set("Kd", request[0], request[1])

    def _get_k_p(self):
        """Get proportionnal coefficient of PID corrector."""
        return self.get("Kp")

    def _set_k_p(self, request):
        """Set proportionnal coefficient of PID corrector."""
        self.set("Kd", request[0], request[1])

    def _get_motor_number(self):
        """Get joint's motor number."""
        return self.get("MotorNumber")

    def _set_motor_number(self, request):
        """Set joint's motor number."""
        self.set("MotorNumber", request[0], request[1])

    def _get_pwm_value(self):
        """Get joint motor PWM value."""
        return self.get("PWMValue")

    def _set_pwm_value(self, request):
        """Set joint motor PWM value."""
        self.set("PWMValue", request[0], request[1])

    max_current = property(_get_max_current, _set_max_current)
    invert_control_direction = property(
        _get_invert_control_direction,
        _set_invert_control_direction
    )
    k_d = property(_get_k_d, _set_k_d)
    k_i = property(_get_k_i, _set_k_i)
    k_p = property(_get_k_p, _set_k_p)
    motor_number = property(_get_motor_number, _set_motor_number)
    pwm_value = property(_get_pwm_value, _set_pwm_value)

    def trapeze(self, max_speed_proportion, ta, tv, sens="positive", second_invert_trapeze=False):
        """
        The wheel makes a trapezoidal speed profile.
        [ta, tv] must be given in milliseconds.
        """
        if sens == "positive":
            speed_command = max_speed_proportion * self.maximum
        else:
            speed_command = max_speed_proportion * self.minimum
        # defining the trapeze
        self.value = [[[speed_command, self.dcm.getTime(ta)]], "ClearAll"]
        self.value = [[[speed_command, self.dcm.getTime(ta + tv)]], "Merge"]
        self.value = [[[0.0, self.dcm.getTime(2 * ta + tv)]], "Merge"]
        if second_invert_trapeze is True:
            offset = 2 * ta + tv
            self.value = \
                [[[-speed_command, self.dcm.getTime(offset + ta)]], "Merge"]
            self.value = \
                [[[-speed_command, self.dcm.getTime(
                    offset + ta + tv)]], "Merge"]
            self.value = \
                [[[0.0, self.dcm.getTime(2 * offset)]], "Merge"]


class WheelSpeedSensor(SubDevice):

    """
    Describes wheels speed sensor.
    ShortName can be in ["WheelFR","WheelFL","WheelB"].
    """

    def __init__(self, dcm, mem, short_name):
        SubDevice.__init__(self, dcm, mem, short_name)
        self.short_name = short_name
        self.name = short_name + "/Speed/Sensor"

    def _get_gear_ratio(self):
        """Get geat ratio."""
        return self.get("GearRatio")

    def _set_gear_ratio(self, request):
        """Set geat ratio."""
        self.set("GearRatio", request[0], request[1])

    def _get_limit(self):
        """Get position sensor limit."""
        return self.get("Limit")

    def _set_limit(self, request):
        """Set position sensor limit."""
        self.set("Limit", request[0], request[1])

    def _get_sensor_type(self):
        """Get sensor type."""
        return self.get("SensorType")

    def _set_sensor_type(self, request):
        """Set sensor type."""
        self.set("SensorType", request[0], request[1])

    def _get_joint_zero_position(self):
        """Get joint zero position."""
        return self.get("jointZeroPosition")

    def _set_joint_zero_position(self, request):
        """Set joint zero position."""
        self.set("jointZeroPosition", request[0], request[1])

    def _get_position_chain_mre_joint(self):
        """Get position chain MRE joint."""
        return self.get("positionChainMREJoint")

    def _set_position_chain_mre_joint(self, request):
        """Set position chain MRE joint."""
        self.set("positionChainMREJoint", request[0], request[1])

    def _get_position_chain_mre_motor(self):
        """Get position chain MRE motor."""
        return self.get("positionChainMREMotor")

    def _set_position_chain_mre_motor(self, request):
        """Set position chain MRE motor."""
        self.set("positionChainMREMotor", request[0], request[1])

    gear_ratio = property(_get_gear_ratio, _set_gear_ratio)
    limit = property(_get_limit, _set_limit)
    sensor_type = property(_get_sensor_type, _set_sensor_type)
    joint_zero_position = property(
        _get_joint_zero_position,
        _set_joint_zero_position)
    position_chain_mre_joint = property(
        _get_position_chain_mre_joint,
        _set_position_chain_mre_joint)
    position_chain_mre_motor = property(
        _get_position_chain_mre_motor,
        _set_position_chain_mre_motor)


class WheelTemperatureSensor(SubDevice):

    """
    Describes wheels speed actuator.
    ShortName must be in ["WheelFR","WheelFL","WheelB"].
    """

    def __init__(self, dcm, mem, short_name):
        SubDevice.__init__(self, dcm, mem, short_name)
        self.short_name = short_name
        self.name = short_name + "/Temperature/Sensor"

    def _get_adress_temperature_sensor(self):
        """Get adress temperature sensor."""
        return self.get("AdressTemperatureSensor")

    def _set_adress_temperature_sensor(self, request):
        """Set adress temperature sensor."""
        self.set("AdressTemperatureSensor", request[0], request[1])

    def _get_other_motor_transmission(self):
        """Get other motor transmission."""
        return self.get("OtherMotorTransmission")

    def _set_other_motor_transmission(self, request):
        """Set other motor transmission."""
        self.set("OtherMotorTransmission", request[0], request[1])

    def _get_start_temperature(self):
        """Get start temperature."""
        return self.get("StartTemperature")

    def _set_start_temperature(self, request):
        """Set start temperature."""
        self.set("StartTemperature", request[0], request[1])

    def _get_temperature_sensor_type(self):
        """Get temperature sensor type."""
        return self.get("TemperatureSensorType")

    def _set_temperature_sensor_type(self, request):
        """Set temperature sensor type."""
        self.set("TemperatureSensorType", request[0], request[1])

    def _get_thermal_resistance(self):
        """Get thermal resistance."""
        return self.get("ThermalResistance")

    def _set_thermal_resistance(self, request):
        """Set thermal resistance."""
        self.set("ThermalResistance", request[0], request[1])

    def _get_motor_model(self):
        """Get motor_model."""
        return self.get("motorModel")

    def _set_motor_model(self, request):
        """Set motor_model."""
        self.set("motorModel", request[0], request[1])

    def _get_ambiant_temperature(self):
        """Get ambiant temperature."""
        return self.get("AmbiantTemperature")

    def _set_ambiant_temperature(self, request):
        """Set ambiant temperature."""
        self.set("AmbiantTemperature", request[0], request[1])

    def _get_status(self):
        """Get subdevice status."""
        return self.get("Status")

    def _set_status(self, request):
        """Set subdevice status."""
        self.set("Status", request[0], request[1])

    def _get_thermal_time_constant(self):
        """Get thermal time constant."""
        return self.get("ThermalTimeConstant")

    def _set_thermal_time_constant(self, request):
        """Set thermal time constant."""
        self.set("ThermalTimeConstant", request[0], request[1])

    def _get_winding_resistance(self):
        """Get winding resistance."""
        return self.get("WindingResistance")

    def _set_winding_resistance(self, request):
        """Set winding resistance."""
        self.set("WindingResistance", request[0], request[1])

    adress_temperature_sensor = property(
        _get_adress_temperature_sensor,
        _set_adress_temperature_sensor)
    other_motor_transmission = property(
        _get_other_motor_transmission,
        _set_other_motor_transmission)
    start_temperature = property(
        _get_start_temperature,
        _set_start_temperature)
    temperature_sensor_type = property(
        _get_temperature_sensor_type,
        _set_temperature_sensor_type)
    thermal_resistance = property(
        _get_thermal_resistance,
        _set_thermal_resistance)
    motor_model = property(_get_motor_model, _set_motor_model)
    ambiant_temperature = property(
        _get_ambiant_temperature,
        _set_ambiant_temperature)
    status = property(_get_status, _set_status)
    thermal_time_constant = property(
        _get_thermal_time_constant,
        _set_thermal_time_constant)
    winding_resistance = property(
        _get_winding_resistance,
        _set_winding_resistance)


class WheelStiffnessActuator(SubDevice):

    """
    Class which defines a wheel stiffness characterized by :
    - its stiffness decrease rate
    ShortName must be in ["WheelFR","WheelFL","WheelB"].
    """

    def __init__(self, dcm, mem, short_name):
        SubDevice.__init__(self, dcm, mem, short_name)
        self.short_name = short_name
        self.name = short_name + "/Stiffness/Actuator"

    def _get_stiffness_decrease_rate(self):
        """Get stiffness decrease rate."""
        return self.get("stiffnessDecreaseRate")

    def _set_stiffness_decrease_rate(self, request):
        """Get stiffness decrease rate."""
        self.set("stiffnessDecreaseRate", request[0], request[1])

    stiffness_decrease_rate = property(
        _get_stiffness_decrease_rate,
        _set_stiffness_decrease_rate)


class WheelCurrentSensor(SubDevice):

    """
    Class which defines a wheel characterized by :
    - its current type
    - its shunt resistance
    """

    def __init__(self, dcm, mem, short_name):
        SubDevice.__init__(self, dcm, mem, short_name)
        self.short_name = short_name
        self.name = short_name + "/ElectricCurrent/Sensor"

    def _get_current_type(self):
        """Get current type."""
        return self.get("CurrentType")

    def _set_current_type(self, request):
        """Set current type."""
        self.set("CurrentType", request[0], request[1])

    def _get_shunt_resistance(self):
        """Get shunt resistance value."""
        return self.get("ShuntResistance")

    def _set_shunt_resistance(self, request):
        """Set shunt resistance value."""
        self.set("ShuntResistance", request[0], request[1])

    current_type = property(_get_current_type, _set_current_type)
    shunt_resistance = property(_get_shunt_resistance, _set_shunt_resistance)


class WheelsMotion(object):

    """Wheels control class."""

    def __init__(self, dcm, mem, vmax):
        self.dcm = dcm
        self.mem = mem
        self.vmax = vmax

        self.wheelfr_speed_actuator = WheelSpeedActuator(dcm, mem, "WheelFR")
        self.wheelfl_speed_actuator = WheelSpeedActuator(dcm, mem, "WheelFL")
        self.wheelb_speed_actuator = WheelSpeedActuator(dcm, mem, "WheelB")

        self.r_roue = 0.07  # m
        self.r_cercle = 0.1762  # m
        # rad - absolute angle between front wheels x axes and robot x axis =
        # rad(90-(123.2058/2)) .
        self.angle_wheels_robot = 0.49562289301808176428859739121848
                                                                     # 123.2058
                                                                     # is the
                                                                     # angle
                                                                     # between
                                                                     # the y
                                                                     # axis of
                                                                     # the two
                                                                     # front
                                                                     # wheels
                                                                     # (Doc
                                                                     # Pepper).
        self.gamma_a = 0.2  # m.s-2
        self.gamma_f = 0.2  # m.s-2
        self.speed = self.vmax * cos(self.angle_wheels_robot) / self.r_roue
        self.t_a = self.vmax / self.gamma_a  # s
        self.t_f = self.vmax / self.gamma_f  # s

    def stiff_wheels(self, wheels_list, value):
        """Set stiffness to 1.0 for wheel names in wheels_list."""
        for wheel_name in wheels_list:
            wheel_stiff_act = \
                WheelStiffnessActuator(self.dcm, self.mem, wheel_name)
            wheel_stiff_act.qvalue = (value, 0.0)

    def move_x(self, distance, wait=True):
        """The robot goes forward for 'distance' meters"""
        t_v = (abs(distance) - (0.5 * self.gamma_a * self.t_a * self.t_a) -
              (0.5 * self.gamma_f * self.t_f * self.t_f)) / self.vmax
        if t_v <= 0:
            print "temps a vitesse constante nul"
        else:
            t1 = self.t_a
            t2 = t1 + t_v
            t3 = t2 + self.t_f

            self.stiff_wheels(["WheelFR", "WheelFL"], 1.0)

            if distance < 0:
                speed = -self.speed
            else:
                speed = self.speed

            timed_commands_wheelfr = [
                (0.0, 0),
                (-speed, 1000 * t1),
                (-speed, 1000 * t2),
                (0.0, 1000 * t3)]

            timed_commands_wheelfl = [
                (0.0, 0),
                (speed, 1000 * t1),
                (speed, 1000 * t2),
                (0.0, 1000 * t3)]

            self.wheelfr_speed_actuator.mqvalue = timed_commands_wheelfr
            self.wheelfl_speed_actuator.mqvalue = timed_commands_wheelfl

            if wait:
                tools.wait(self.dcm, 1000 * t3)
                self.stiff_wheels(["WheelFR", "WheelFL"], 0.0)

    def move_y(self, distance, wait=True):
        """The robot goes forward for 'distance' meters"""
        t_v = (abs(distance) - (0.5 * self.gamma_a * self.t_a * self.t_a) -
              (0.5 * self.gamma_f * self.t_f * self.t_f)) / self.vmax
        if t_v <= 0:
            print "temps a vitesse constante nul"
        else:
            t1 = self.t_a
            t2 = t1 + t_v
            t3 = t2 + self.t_f

            self.stiff_wheels(["WheelFR", "WheelFL", "WheelB"], 1.0)

            if distance < 0:
                self.speed = -self.speed

            timed_commands_wheelfr = [
                (0.0, 0),
                (-0.5 * self.speed, 1000 * t1),
                (-0.5 * self.speed, 1000 * t2),
                (0.0, 1000 * t3)]

            timed_commands_wheelfl = [
                (0.0, 0),
                (-0.5 * self.speed, 1000 * t1),
                (-0.5 * self.speed, 1000 * t2),
                (0.0, 1000 * t3)]

            timed_commands_wheelb = [
                (0.0, 0),
                (self.speed, 1000 * t1),
                (self.speed, 1000 * t2),
                (0.0, 1000 * t3)]

            self.wheelfr_speed_actuator.mqvalue = timed_commands_wheelfr
            self.wheelfl_speed_actuator.mqvalue = timed_commands_wheelfl
            self.wheelb_speed_actuator.mqvalue = timed_commands_wheelb

            if wait:
                tools.wait(self.dcm, 1000 * t3)
                self.stiff_wheels(["WheelFR", "WheelFL", "WheelB"], 0.0)

    def rotate(self, nb_tour, wait=True):
        theta_tot = (self.r_cercle / self.r_roue) * 2 * pi * nb_tour
        t_v = (abs(theta_tot) - (0.5 * self.gamma_a * self.t_a * self.t_a) -
              (0.5 * self.gamma_f * self.t_f * self.t_f)) / self.speed

        if t_v <= 0:
            print "temps a vitesse constante nul"
        else:
            t1 = self.t_a
            t2 = t1 + t_v
            t3 = t2 + self.t_f

            self.stiff_wheels(["WheelFR", "WheelFL", "WheelB"], 1.0)

            if nb_tour < 0:
                self.speed = -self.speed

            timed_commands = [
                (0.0, 0),
                (self.speed, 1000 * t1),
                (self.speed, 1000 * t2),
                (0.0, 1000 * t3)]

            self.wheelfr_speed_actuator.mqvalue = timed_commands
            self.wheelfl_speed_actuator.mqvalue = timed_commands
            self.wheelb_speed_actuator.mqvalue = timed_commands

            if wait:
                tools.wait(self.dcm, 1000 * t3)
                self.stiff_wheels(["WheelFR", "WheelFL", "WheelB"], 0.0)


class Switch(SubDevice):

    """
    Class which defines a switch hardness characterized by:
    - the sub-device only
    """

    def __init__(self, dcm, mem, short_name):
        SubDevice.__init__(self, dcm, mem, short_name)
        self.short_name = short_name

        if short_name == "ChestBoard":
            self.name = short_name + "/Button/Sensor"
        else:
            self.name = short_name + "/Sensor"


class Touch(SubDevice):

    """To commment."""

    def __init__(self, dcm, mem, short_name):
        SubDevice.__init__(self, dcm, mem, short_name)
        self.short_name = short_name
        self.name = short_name + "/Sensor"


class Led(SubDevice):

    """Class which describes a Led for NAO robot."""

    def __init__(self, dcm, mem, short_name):
        SubDevice.__init__(self, dcm, mem, short_name)
        self.short_name = short_name
        self.name = short_name + "/Actuator"

    def locate(self):
        """
        This method returns a tuple defining a box on camera picture where
        the led is located
        """
        led_pos_name = tools.reduce_name(
            self.short_name,
            "/",
            "Led",
            "Red",
            "Green",
            "Blue"
        )
        led_pos = tools.read_int_tuple(
            "Configuration/leds.cfg",
            "LEDPos",
            led_pos_name
        )
        return led_pos


class FSR(SubDevice):

    """Class which describes FSR parameters for NAO robot."""

    def __init__(self, dcm, mem, short_name):
        SubDevice.__init__(self, dcm, mem, short_name)
        self.short_name = short_name
        self.name = short_name + "/Sensor"

    def _get_x_position(self):
        """Get FSR x position."""
        return self.get("XPosition")

    def _set_x_position(self, request):
        """Get FSR x position."""
        self.set("XPosition", request[0], request[1])

    def _get_y_position(self):
        """Get FSR y position."""
        return self.get("YPosition")

    def _set_y_position(self, request):
        """Set FSR y position."""
        self.set("YPosition", request[0], request[1])

    xPosition = property(_get_x_position, _set_x_position)
    yPosition = property(_get_y_position, _set_y_position)


class CenterOfPressure(SubDevice):

    """
    Class for NAO robot.
    Class which describes centre of pressure for NAO robot.
    """

    def __init__(self, dcm, mem, short_name):
        SubDevice.__init__(self, dcm, mem, short_name)
        self.short_name = short_name
        self.name = short_name + "/Sensor"


class TotalWeight(SubDevice):

    """
    Class for NAO robot.
    Class which describes total weight.
    """

    def __init__(self, dcm, mem, short_name):
        SubDevice.__init__(self, dcm, mem, short_name)
        self.short_name = short_name
        self.name = short_name + "/Sensor"


class Inertial(SubDevice):

    """
    Class for NAO robot.
    It describes inertial sensor.
    """

    def __init__(self, dcm, mem, short_name):
        SubDevice.__init__(self, dcm, mem, short_name)
        self.short_name = short_name

        self.sens_type = tools.reduce_name(
            self.short_name,
            "/",
            "InertialSensor")
        for axis in ("X", "Y", "Z"):
            if axis in self.sens_type:
                self.sens_type = self.sens_type.replace(axis, "")

        self.name = short_name + "/Sensor"

# MultifuseBoard classes


class MultiFuseBoardAmbiantTemperature(SubDevice):

    """
    Class for JULIETTE robot.
    It describes the ambiant temperature sensor linked to the MultiFuseBoard.
    """

    def __init__(self, dcm, mem, short_name="MultiFuseBoard"):
        SubDevice.__init__(self, dcm, mem, short_name)
        self.name = short_name + "/AmbiantTemperature/Sensor"
        self.header_name = "MultifuseBoard_Ambiant_Temperature"


class MultiFuseBoardTotalCurrent(SubDevice):

    """
    Class for JULIETTE robot.
    It describes the total current into the MultiFuseBoard device.
    """

    def __init__(self, dcm, mem, short_name="MultiFuseBoard"):
        SubDevice.__init__(self, dcm, mem, short_name)
        self.name = short_name + "/CurrentTotal/Sensor"
        self.header_name = "MultifuseBoard_Total_Current"


class FuseTemperature(SubDevice):

    """
    Class for JULIETTE robot.
    It describes the fuse temperature.
    Architecture scenario 4.
    Part can be one of the following assembly:
    - "UN" = Neck
    - "UR" = Right Arm
    - "UL" = Left Arm
    - "DW" = Bottom
    [Object creation example]
    fuseTemperature = FuseTemperature(dcm, mem, "UR")
    """

    def __init__(self, dcm, mem, part):
        self.short_name = "MultiFuseBoard"
        self.physical_quantity = "Temperature"
        SubDevice.__init__(self, dcm, mem, self.short_name)
        self.part = part
        self.name = self.short_name + "/Temperature" + str(part) + "/Sensor"
        self.header_name = "_".join(
            [
                "Fuse",
                str(self.part),
                str(self.physical_quantity)
            ]
        )

    def _get_status(self):
        """Get fuse temperature status."""
        return self.get("Status")

    def _set_status(self, request):
        """Set fuse temperature status."""
        self.set("Status", request[0], request[1])

    status = property(_get_status, _set_status)


class FuseCurrent(SubDevice):

    """
    Class for JULIETTE robot.
    It describes the fuse current.
    Architecture scenario 4.
    part can be one of the following assembly:
    - "UN" = Neck
    - "UR" = Right Arm
    - "UL" = Left Arm
    - "DW" = Bottom
    [Object creation example]
    fuseCurrent = FuseCurrent(dcm, mem, "UN")
    """

    def __init__(self, dcm, mem, part):
        self.short_name = "MultiFuseBoard"
        self.physical_quantity = "Current"
        SubDevice.__init__(self, dcm, mem, self.short_name)
        self.part = part
        self.name = self.short_name + "/Current" + part + "/Sensor"
        self.header_name = "_".join(
            [
                "Fuse",
                str(self.part),
                str(self.physical_quantity)
            ]
        )


class FuseVoltage(SubDevice):

    """
    Class for JULIETTE robot.
    It describes the fuse current.
    Architecture scenario 4.
    part can be one of the following assembly:
    - "UN" = Neck
    - "UR" = Right Arm
    - "UL" = Left Arm
    - "DW" = Bottom
    [Object creation example]
    fuseVoltage = FuseVoltage(dcm, mem, "DW")
    """

    def __init__(self, dcm, mem, part):
        self.short_name = "MultiFuseBoard"
        self.physical_quantity = "Voltage"
        SubDevice.__init__(self, dcm, mem, self.short_name)
        self.part = part
        self.name = self.short_name + "/Voltage" + part + "/Sensor"
        self.header_name = "_".join(
            [
                "Fuse",
                str(self.part),
                str(self.physical_quantity)
            ]
        )


class FuseResistor(SubDevice):

    """
    Class for JULIETTE robot.
    It describes the fuse current.
    Architecture scenario 4.
    part can be one of the following assembly:
    - "UN" = Neck
    - "UR" = Right Arm
    - "UL" = Left Arm
    - "DW" = Bottom
    [Object creation example]
    fuseResistor = FuseResistor(dcm, mem, "UN")
    """

    def __init__(self, dcm, mem, part):
        self.short_name = "MultiFuseBoard"
        SubDevice.__init__(self, dcm, mem, self.short_name)
        self.part = part
        self.name = self.short_name + "/Resistor" + part + "/Sensor"

# Fan classes


class FanHardnessActuator(SubDevice):

    """
    Class for JULIETTE robot.
    It describes fanboard actuator.
    [Object creation example]
    fanHardnessActuator = FanHardnessActuator(dcm, mem)
    """

    def __init__(self, dcm, mem):
        self.short_name = "FanBoard"
        self.header_name = self.short_name + "ActuatorValue"
        SubDevice.__init__(self, dcm, mem, self.short_name)
        self.name = self.short_name + "/Hardness/Actuator"


class FanFrequencySensor(SubDevice):

    """
    Class for JULIETTE robot.
    It describes the fans frequency sensors.
    part can be one of the following assembly:
    - "Right"
    - "Mid"
    - "Left"
    [Object creation example]
    fanFrequencySensor = FanFrequencySensor(dcm, mem, "Right")
    """

    def __init__(self, dcm, mem, part):
        self.short_name = "FanBoard"
        SubDevice.__init__(self, dcm, mem, self.short_name)
        self.part = part
        self.header_name = self.part + "FanFrequency"
        self.name = self.short_name + "/Frequency" + self.part + "/Sensor"


class FanStatus(SubDevice):

    """
    Class for JULIETTE robot.
    It describes fan status.
    [Object creation example]
    fanStatus = FanStatus(dcm, mem)
    """

    def __init__(self, dcm, mem):
        self.short_name = "FanBoard"
        SubDevice.__init__(self, dcm, mem, self.short_name)
        self.name = self.short_name + "/Fan"
        self.header_name = "FanStatus"

    def _get_status(self):
        """Get fan status."""
        return self.get("Status")

    def _set_status(self, request):
        """Set fan status."""
        self.set("Status", request[0], request[1])

    status = property(_get_status, _set_status)


class Laser(SubDevice):

    """
    Class for JULIETTE robot.
    It describes laser sensor.
    [Object creation example]
    laser = Laser(dcm, mem, "Front/Horizontal/Seg01/X/Sensor")
    """

    def __init__(self, dcm, mem, key):
        SubDevice.__init__(self, dcm, mem, key)
        self.name = "Platform/LaserSensor/" + key


class InertialSensorBase(SubDevice):

    """
    Class for JULIETTE robot.
    It describes InertialSensorBase sensor.
    [Object creation example]
    inertial_sensor_base = InertialSensorBase(dcm, mem, "AngleX")
    """

    def __init__(self, dcm, mem, key):
        SubDevice.__init__(self, dcm, mem, key)
        self.name = "InertialSensorBase/" + key + "/Sensor"


class Sonar(SubDevice):

    """
    Class for JULIETTE robot.
    It describes sonar sensor.
    [Object creation example]
    sonar = Sonar(dcm, mem, "Front")
    """

    def __init__(self, dcm, mem, key):
        SubDevice.__init__(self, dcm, mem, key)
        self.name = "Platform/" + key + "/Sonar/Sensor"


class Bumper(SubDevice):

    """
    Class for JULIETTE robot.
    It describes bumpers sensors.
    [Object creation example]
    bumper = Bumper(dcm, mem, "Back")
    """

    def __init__(self, dcm, mem, key):
        SubDevice.__init__(self, dcm, mem, key)
        self.name = "Platform/" + key + "/Bumper/Sensor"


class ChargingStationSensor(SubDevice):

    """
    Class for JULIETTE robot.
    """

    def __init__(self, dcm, mem, short_name="Platform"):
        self.short_name = short_name
        SubDevice.__init__(self, dcm, mem, self.short_name)
        self.name = self.short_name + "/RobotOnChargingStation/Sensor"


class BatteryCurrentSensor(SubDevice):

    """
    Class for JULIETTE robot.
    """

    def __init__(self, dcm, mem, short_name="Battery"):
        self.short_name = short_name
        SubDevice.__init__(self, dcm, mem, self.short_name)
        self.name = self.short_name + "/Current/Sensor"


class BatteryChargeSensor(SubDevice):

    """
    Class for JULIETTE robot with VARTA battery.
    It describes the battery charge sensor.
    """

    def __init__(self, dcm, mem):
        self.short_name = "Battery"
        SubDevice.__init__(self, dcm, mem, self.short_name)
        self.name = self.short_name + "/Charge/Sensor"

    def _get_age(self):
        """Get subdevice's age from ALMemory."""
        return self.get("Age")

    def _set_age(self, request):
        """Set subdevice's age"""
        self.set("Age", request[0], request[1])

    def _get_average_current(self):
        """Get subdevice's average_current from ALMemory."""
        return self.get("AverageCurrent")

    def _set_average_current(self, request):
        """Set subdevice's average_current"""
        self.set("AverageCurrent", request[0], request[1])

    def _get_battery_low(self):
        """Get subdevice's battery low indication from ALMemory."""
        return self.get("BatteryLow")

    def _set_battery_low(self, request):
        """Set subdevice's battery low indication"""
        self.set("BatteryLow", request[0], request[1])

    def _get_cedv(self):
        """Get subdevice's cedv from ALMemory."""
        return self.get("CEDV")

    def _set_cedv(self, request):
        """Set subdevice's cedv"""
        self.set("CEDV", request[0], request[1])

    def _get_cell_count(self):
        """Get subdevice's cell count from ALMemory."""
        return self.get("CellCount")

    def _set_cell_count(self, request):
        """Set subdevice's cell count"""
        self.set("CellCount", request[0], request[1])

    def _get_cell_value(self):
        """Get subdevice's cell value from ALMemory."""
        return self.get("CellValue")

    def _set_cell_value(self, request):
        """Set subdevice's cell value"""
        self.set("CellValue", request[0], request[1])

    def _get_cell_voltage_max(self):
        """Get subdevice's cell voltage max from ALMemory."""
        return self.get("CellVoltageMax")

    def _set_cell_voltage_max(self, request):
        """Set subdevice's cell voltage max"""
        self.set("CellVoltageMax", request[0], request[1])

    def _get_cell_voltage_min(self):
        """Get subdevice's cell voltage min from ALMemory."""
        return self.get("CellVoltageMin")

    def _set_cell_voltage_min(self, request):
        """Set subdevice's cell voltage min"""
        self.set("CellVoltageMin", request[0], request[1])

    def _get_charge(self):
        """Get subdevice's charge from ALMemory."""
        return self.get("Charge")

    def _set_charge(self, request):
        """Set subdevice's charge"""
        self.set("Charge", request[0], request[1])

    def _get_charging(self):
        """Get subdevice's charging indication from ALMemory."""
        return self.get("Charging")

    def _set_charging(self, request):
        """Set subdevice's charging indication"""
        self.set("Charging", request[0], request[1])

    def _get_cycle_count(self):
        """Get subdevice's cycles count from ALMemory."""
        return self.get("CyclesCount")

    def _set_cycle_count(self, request):
        """Set subdevice's cycles count"""
        self.set("CyclesCount", request[0], request[1])

    def _get_end_of_life(self):
        """Get subdevice's end of life from ALMemory."""
        return self.get("EndOfLife")

    def _set_end_of_life(self, request):
        """Set subdevice's end of life"""
        self.set("EndOfLife", request[0], request[1])

    def _get_flags(self):
        """Get subdevice's flags from ALMemory."""
        return self.get("Flags")

    def _set_flags(self, request):
        """Set subdevice's flags"""
        self.set("Flags", request[0], request[1])

    def _get_full_charge_capacity(self):
        """Get subdevice's full charge capacity from ALMemory."""
        return self.get("FullChargeCapacity")

    def _set_full_charge_capacity(self, request):
        """Set subdevice's full charge capacity"""
        self.set("FullChargeCapacity", request[0], request[1])

    def _get_remaining_capacity(self):
        """Get subdevice's remaining capacity from ALMemory."""
        return self.get("RemainingCapacity")

    def _set_remaining_capacity(self, request):
        """Set subdevice's remaining capacity"""
        self.set("RemainingCapacity", request[0], request[1])

    def _get_self_discharge_current(self):
        """Get subdevice's self discharge current from ALMemory."""
        return self.get("SelfDischargeCurrent")

    def _set_self_discharge_current(self, request):
        """Set subdevice's self discharge current"""
        self.set("SelfDischargeCurrent", request[0], request[1])

    def _get_state_of_health(self):
        """Get subdevice's state of health from ALMemory."""
        return self.get("StateOfHealth")

    def _set_state_of_health(self, request):
        """Set subdevice's state of health"""
        self.set("StateOfHealth", request[0], request[1])

    def _get_status(self):
        """Get subdevice's status from ALMemory."""
        return self.get("Status")

    def _set_status(self, request):
        """Set subdevice's status"""
        self.set("Status", request[0], request[1])

    def _get_time_to_empty(self):
        """Get subdevice's TTE from ALMemory."""
        return self.get("TimeToEmpty")

    def _set_time_to_empty(self, request):
        """Set subdevice's TTE"""
        self.set("TimeToEmpty", request[0], request[1])

    def _get_time_to_full(self):
        """Get subdevice's TTF from ALMemory."""
        return self.get("TimeToFull")

    def _set_time_to_full(self, request):
        """Set subdevice's TTF"""
        self.set("TimeToFull", request[0], request[1])

    def _get_total_voltage(self):
        """Get subdevice's total voltage from ALMemory."""
        return self.get("TotalVoltage")

    def _set_total_voltage(self, request):
        """Set subdevice's total voltage"""
        self.set("TotalVoltage", request[0], request[1])

    age = property(_get_age, _set_age)
    average_current = property(_get_average_current, _set_average_current)
    battery_low = property(_get_battery_low, _set_battery_low)
    cedv = property(_get_cedv, _set_cedv)
    cell_count = property(_get_cell_count, _set_cell_count)
    cell_value = property(_get_cell_value, _set_cell_value)
    cell_voltage_max = property(_get_cell_voltage_max, _set_cell_voltage_max)
    cell_voltage_min = property(_get_cell_voltage_min, _set_cell_voltage_min)
    charge = property(_get_charge, _set_charge)
    charging = property(_get_charging, _set_charging)
    cycle_count = property(_get_cycle_count, _set_cycle_count)
    end_of_life = property(_get_end_of_life, _set_end_of_life)
    flags = property(_get_flags, _set_flags)
    full_charge_capacity = property(
        _get_full_charge_capacity, _set_full_charge_capacity)
    remaining_capacity = property(
        _get_remaining_capacity, _set_remaining_capacity)
    self_discharge_current = property(
        _get_self_discharge_current, _set_self_discharge_current)
    state_of_health = property(_get_state_of_health, _set_state_of_health)
    status = property(_get_status, _set_status)
    time_to_empty = property(_get_time_to_empty, _set_time_to_empty)
    time_to_full = property(_get_time_to_full, _set_time_to_full)
    total_voltage = property(_get_total_voltage, _set_total_voltage)
