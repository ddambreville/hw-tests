If the ALMemory key "RobotConfig/Head/MinMaxChangeAllowed" does not exist or
is not set to 1, test will fail without going into the test loop.

This key is essential to allow robot to shift its software mechanical stop and
be able to force against its real mechanical stops. The aim being to make the
electric current rise into the concerned joints.

[How to]
The manipulation consists in adding the key into DeviceHeadInternalGeode.xml
and restart naoqi and the HAL.

1°) ssh nao@<your_robot_ip>
2°) Enter root pwd
3°) nano /media/internal/DeviceHeadInternalGeode.xml
4°) Add the following line at the end :
<Preference name="Key14" memoryName="RobotConfig/Head/MinMaxChangeAllowed" description="" value="1" type="string" />
5°) Stop naoqi (nao stop)
6°) Stop HAL (/etc/init.d/hald stop)
7°) Start HAL (/etc/init.d/hald start)
8°) Start naoqi (nao start)
