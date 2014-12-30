# -*- encoding: UTF-8 -*-
#!/usr/bin/python

'''
@author: Safran Engineering Services - Thomas CHARLES
@contact: tcharles@presta.aldebaran-robotics.fr
@copyright : Aldebaran Robotics 2014
@version: [creation][11/06/2014]
@summary: brakes dynamic performances using ALMotion module.
'''

# -----------------------------------        
# ------------- Import --------------
# -----------------------------------

from naoqi import ALProxy
import multi_logger
import argparse
import math
import datetime
import time

# ------------------------------------------------        
# ------------- Joint control class --------------
# ------------------------------------------------

class Joint(object):
    """
    Allows to {control/accede to} the following joint parameters:
    - position [rad] (set & get)
    - stiffness (set & get)
    - mechanical stop min [rad] (get only)
    - mechanical stop max [rad] (get only)
    - temperature [degrees] (get only)
    """
    def __init__(self, motion, mem, jointName):
        self.motion = motion
        self.mem = mem
        self.jointName = jointName
        self.prefixe = "Device/SubDeviceList/"
    
    def _set_position(self, request):
        """request is a Tuple : (angle[rad], speed(between 0 and 1) -> percentage of max speed allowed by ALMotion)"""
        self.motion.post.angleInterpolationWithSpeed(self.jointName, request[0], request[1])
        
    def _set_position_bloquant(self, request):
        """request is a Tuple : (angle[rad], speed(between 0 and 1) -> percentage of max speed allowed by ALMotion)"""
        self.motion.angleInterpolationWithSpeed(self.jointName, request[0], request[1])
    
    def _get_position(self):
        """get position in [rad] from ALMemory"""
        return float(self.mem.getData(self.prefixe+self.jointName+"/Position/Sensor/Value"))
    
    def _set_stiffness(self, request):
        """
        Set joint stiffness. Value must be between [0,1].
        To set HipPitch or KneePitch stiffness while the joint is moving, you have to disable
        the brake protection.
        """
        self.motion._setStiffnesses(self.jointName, request)
        
    def _get_stiffness(self):
        """Retrieve robot's stiffness from ALMemory."""
        return float(self.mem.getData(self.prefixe+self.jointName+"/Position/Sensor/Value"))
    
    def _get_mechanicalStopMin(self):
        """Retrieve joint's minimal mechanical stop."""
        return float(self.mem.getData(self.prefixe+self.jointName+"/Position/Actuator/Min"))
        
    def _get_mechanicalStopMax(self):
        """Retrieve joint's maximal mechanical stop."""
        return float(self.mem.getData(self.prefixe+self.jointName+"/Position/Actuator/Max"))
        
    def _get_temperature(self):
        """Retrieve joint temperature."""
        return float(self.mem.getData(self.prefixe+self.jointName+"/Temperature/Sensor/Value"))
    
    position = property(_get_position, _set_position)
    positionbloquant = property(_get_position, _set_position_bloquant)
    stiffness = property(_get_stiffness, _set_stiffness)
    mechanicalStopMin = property(_get_mechanicalStopMin)
    mechanicalStopMax = property(_get_mechanicalStopMax)
    temperature = property(_get_temperature)
        
# ------------------------------------------------        
# ------------- Motion dynamic test --------------
# ------------------------------------------------

class MotionDynamicBrakesTest(object):
    def __init__(self, ip, jointName, direction, cyclingBrakingAngle, cycleNumber):
        """Test parameters"""
        # attributes to be parsed in the main
        self.ip = ip
        self.jointName = jointName
        self.direction = direction
        self.cyclingBrakingAngleDegrees = cyclingBrakingAngle
        self.nbCyclingDynamicTest = cycleNumber
        # proxy creation
        self.motion = ALProxy("ALMotion", self.ip, 9559)
        self.mem = ALProxy("ALMemory", self.ip, 9559)
        self.system = ALProxy("ALSystem", self.ip, 9559)
        # logger parameters
        self.testType = "brakes_dynamic_test_ALMotion"
        self.extension = "csv"
        self.date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.robotName = self.system.robotName()
        self.filePath = "-".join([self.robotName, self.date, self.testType, self.direction])
        self.confFilePath = "multi_logger.cfg"
        self.samplePeriod = 0.02
        self.output = ".".join([self.filePath,self.extension])
        self.decimal = 3
        self.logger = multi_logger.Logger(self.ip, self.confFilePath, self.samplePeriod, self.output, self.decimal)
        # ---------------------------------------------------------------------
        # TEST PARAMETERS - values which can be modified
        # ---------------------------------------------------------------------
        
        # speed
        self.slowSpeed = 0.2
        self.maxSpeed = 1.0
        # mechanical stop protection angles
        self.maxAngleHipDegrees = 55.0
        self.maxAngleKneeDegrees = 30.0
        # hip test start and stop angles
        self.angleMinHip = 30.0
        self.angleMaxHip = 50.0
        # knee test start and stop angles
        self.angleMinKnee = -1.0
        self.angleMaxKnee = 9.0
        # step
        self.step = 2.0
        # max temperature
        self.jointMaxTemperature = 70.0
        
        # ---------------------------------------------------------------------
        self.nbDynaTest = (self.angleMaxHip - self.angleMinHip) / (self.step) + 1
        self.nbDynaTestKnee = (self.angleMaxKnee - self.angleMinKnee) / (self.step) + 1
        
        # joints object creation
        self.principalJoint = Joint(self.motion, self.mem, self.jointName)
        if(self.jointName == "HipPitch"):
            self.secondJoint = Joint(self.motion, self.mem, "KneePitch")
        else:
            self.secondJoint = Joint(self.motion, self.mem, "HipPitch")
        # test parameters adaptation
        # max angle
        if self.jointName == "HipPitch":
            if self.direction == "Positive":
                self.angleMax = -self.angleMaxHip
            else:
                self.angleMax = self.angleMaxHip
        else:
            if direction == "Positive":
                self.angleMax = -self.angleMaxKnee
            else:
                self.angleMax = self.angleMaxKnee
        # min angle
        if self.jointName == "HipPitch":
            if self.direction == "Positive":
                self.angleMin = -self.angleMinHip
            else:
                self.angleMin = self.angleMinHip
        else:
            if self.direction == "Positive":
                self.angleMin = -self.angleMinKnee
            else:
                self.angleMin = self.angleMinKnee
        # step
        if self.direction == "Positive":
            self.step = -self.step
        # nbDynaTest
        if self.jointName == "KneePitch":
            self.nbDynaTest = self.nbDynaTestKnee
        
        # dynamicCyclingTest parameters adaptation
        if self.direction == "Positive":
            self.cyclingBrakingAngleDegrees *= -1        
    
    def wakeUp(self):
        self.motion.wakeUp()
        
    def rest(self):
        self.motion.rest()
        
    def disableBrakesProtection(self):
        self.motion.setMotionConfig([["ENABLE_BRAKES_PROTECTION", False]])
        print("Brakes protection disabled")
        
    def enableBrakesProtection(self):
        self.motion.setMotionConfig([["ENABLE_BRAKES_PROTECTION", True]])
        print("Brakes protection enabled")
        
    def disableArmsExternalProtection(self):
        try:
            self.motion.setExternalCollisionProtectionEnabled("Arms", False)
        except:
            print("---------------------------------------------------------")
            print("Impossible to disable Arms external collision protection")
            print("Check settings in robot's web page")
            print("---------------------------------------------------------")
            
    def enableArmsExternalProtection(self):
        try:
            self.motion.setExternalCollisionProtectionEnabled("Arms", True)
        except:
            print("---------------------------------------------------------")
            print("Impossible to enable Arms external collision protection")
            print("---------------------------------------------------------")
    
    def goToInitialPosition(self):
        time.sleep(5)
        print("going to initial position...")
        if self.direction == "Positive":
            positionToReach = self.principalJoint.mechanicalStopMax
            print positionToReach
        else:
            positionToReach = self.principalJoint.mechanicalStopMin
        self.principalJoint.position = (positionToReach, self.slowSpeed)
        time.sleep(5)
        
    def reachTheOtherSideWithMaxSpeed(self):
        print("reaching the other side with speed")
        if self.direction == "Positive":
            positionToReach = self.principalJoint.mechanicalStopMin
        else:
            positionToReach = self.principalJoint.mechanicalStopMax
        self.principalJoint.position = (positionToReach, self.maxSpeed)
        
    def reachTheOtherSideBraking(self, brakingAngle):
        self.reachTheOtherSideWithMaxSpeed()
        # brake just when the braking angle is reached
        if(self.direction == "Positive"):
            while(self.principalJoint.position > math.radians(brakingAngle)):
                pass
        else:
            while(self.principalJoint.position < math.radians(brakingAngle)):
                pass
        # braking
        self.principalJoint.stiffness = 0.0
        self.secondJoint.stiffness = 0.0
        # retrieving braking angle
        brakingAgnleBefore = self.principalJoint.position
        # wait until braking is finished
        time.sleep(1.0)
        # retrieving braking angle after
        brakingAgnleAfter = self.principalJoint.position
        return (brakingAgnleBefore, brakingAgnleAfter)
    
    def waitTemperatureDecrease(self):
        """If one of the joint temperature reaches the fixed limit, wait until the temperature decreases"""
        if((self.principalJoint.temperature >= self.jointMaxTemperature) or (self.secondJoint.temperature >= self.jointMaxTemperature)):
            print("joint too hot, waiting for temperature to decrease...")
            self.rest()
            while(self.principalJoint.temperature >= self.jointMaxTemperature or self.secondJoint.temperature >= self.jointMaxTemperature):
                pass
                time.sleep(2)
        
    def start(self):
        # initialization
        brakingAngle = self.angleMin
        flag = False
        flagHip = False
        flagKnee = False
        joints = [self.principalJoint, self.secondJoint]
        
        # disabling brakes protection
        self.disableBrakesProtection()
        
        # disable arms external collision protection
        self.disableArmsExternalProtection()
        
        # start log
        self.logger.log()
        
        # test loop
        cptTest = 0
        while(cptTest < self.nbDynaTest and flag is False):
            # robot wakeUp
            self.wakeUp()
            # going to initial position
            self.goToInitialPosition()
            print("Going to the other side and braking at : "+str(brakingAngle)+" degrees")
            # reach the other side at 100% of speed allowed by ALMotion
            braking_info = self.reachTheOtherSideBraking(brakingAngle)
            # giving braking informations
            print("started braking at "+str(math.degrees(braking_info[0]))+"degrees")
            print("stopped braking at "+str(math.degrees(braking_info[1]))+"degrees")
            deltaAlphaDeg = math.degrees(braking_info[1] + braking_info[0])
            print("delta angle = "+str(deltaAlphaDeg))
            # check that it is not out of the technical specifications
            for joint in joints:
                if(joint.jointName == "HipPitch" and abs(math.degrees(joint.position)) >= self.maxAngleHipDegrees):
                    flag = True
                    flagHip = True
                if(joint.jointName == "KneePitch" and abs(math.degrees(joint.position)) >= self.maxAngleKneeDegrees):
                    flag = True
                    flagKnee = True
            if flag is False:
                # increment brake angle if the limit has not been reached
                brakingAngle += self.step
            cptTest += 1
            self.waitTemperatureDecrease()
        
        # out of the loop -> rest position
        self.rest()
        
        # stop log
        self.logger.stop()
        
        # enabling brakes protection
        self.enableBrakesProtection()
        
        # print test result
        if(flagHip is True):
            print("Stopped because Hip out of its Holding Cone")
        if(flagKnee is True):
            print("Stopped because Knee out of its Holding Cone")
        print("Angle max = " + str(brakingAngle))
        
    def startCycling(self):
        # initialization
        brakingAngle = self.cyclingBrakingAngleDegrees
        
        # disabling brakes protection
        self.disableBrakesProtection()
        
        # disable arms external collision protection
        self.disableArmsExternalProtection()
        
        # start log
        self.logger.log()
        
        # test cycling loop
        for i in range(self.nbCyclingDynamicTest):
            # cycle information
            print(" ".join(["cycle number :", str(i+1), "on", str(self.nbCyclingDynamicTest)]))
            # robot wakeUp
            self.wakeUp()
            # going to initial position
            self.goToInitialPosition()
            print(" ".join(["Going to the other side and braking at :", str(brakingAngle), "degrees"]))
            # reach the other side at 100% of speed allowed by ALMotion
            self.reachTheOtherSideBraking(brakingAngle)
            self.waitTemperatureDecrease()
        
        # out of the loop -> rest position
        self.rest()
        
        # stop log
        self.logger.stop()
        
        # enabling brakes protection
        self.enableBrakesProtection()
 
        
# ------------------------------------------------        
# ------------- Motion static test ---------------
# ------------------------------------------------
        
class MotionStaticBrakesTest(MotionDynamicBrakesTest):
    def __init__(self, ip, jointName, direction, initialAngle):
        MotionDynamicBrakesTest.__init__(self, ip, jointName, direction, 0.0, 1)
        self.ip = ip
        self.jointName = "HipPitch"
        self.direction = direction
        self.speed = 0.3
        # ---------------------------------------------------------------------
        # TEST PARAMETERS - values which can be modified
        # ---------------------------------------------------------------------
        self.waitTime = 10.0
        self.limitDeg = 0.5
        self.increment = 1.0
        self.initialAngle = initialAngle
        # ---------------------------------------------------------------------
        # proxy creation
        self.motion = ALProxy("ALMotion", self.ip, 9559)
        self.mem = ALProxy("ALMemory", self.ip, 9559)
        self.hipPitch = Joint(self.motion, self.mem, self.jointName)
        self.kneePitch = Joint(self.motion, self.mem, "KneePitch")
        # test parameters adaptation
        if self.direction == "Positive":
            self.increment = -self.increment
            self.initialAngle = -self.initialAngle
        print("------------TEST PARAMETERS---------------")
        print("increment="+str(self.increment))
        print("angle initial="+str(self.initialAngle))
        print("debut du test...")
        print("------------------------------------------\n\n")
            
    def areJointStatics(self):
        print("checking that no joint in slipping...")
        # Initial HipPitch position
        initialPositionHip = self.hipPitch.position
        initialHipPositionHipDeg = math.degrees(initialPositionHip)
        
        # Initial KneePitch position
        initialPositionKnee = self.kneePitch.position
        initialHipPositionKneeDeg = math.degrees(initialPositionKnee)
        
        # Initial time
        t0 = time.time()
        
        # Control boolean initialization
        hipState = True
        kneeState = True
        state = True
        
        while(time.time() - t0 < self.waitTime and state is True):
            positionHip = self.hipPitch.position
            positionHipDeg = math.degrees(positionHip)
            
            positionKnee = self.kneePitch.position
            positionKneeDeg = math.degrees(positionKnee)
            
            deltaHipDeg = abs(positionHipDeg - initialHipPositionHipDeg)
            deltaKneeDeg = abs(positionKneeDeg - initialHipPositionKneeDeg)
            
            if(deltaHipDeg >= self.limitDeg):
                hipState = False
                state = False
            
            if(deltaKneeDeg >= self.limitDeg):
                kneeState = False
                state = False
                
        return (state, hipState, kneeState)
    
    def closeBrakes(self):
        self.hipPitch.stiffness = 0.0
        self.kneePitch.stiffness = 0.0
    
    def openBrakes(self):
        self.hipPitch.stiffness = 1.0
        self.kneePitch.stiffness = 1.0
        
    def printRealInformations(self):
        print("\n")
        print"[Position information]"
        print("HipPitch position = "+str(round(math.degrees(self.hipPitch.position), 2))+" degrees")
        print("KneePitch position = "+str(round(math.degrees(self.kneePitch.position), 2))+" degrees")
        print"[Temperature information]"
        print("HipPitch temperature = "+str(self.hipPitch.temperature)+"°C")
        print("KneePitch temperature = "+str(self.kneePitch.temperature)+"°C")
        
    def start(self):
        
        # disabling brakes protection
        self.disableBrakesProtection()
        
        # disable arms external collision protection
        self.disableArmsExternalProtection()
        
        # initialization
        flag = True
        angularCommandDeg = self.initialAngle
        angularCommandRad = math.radians(angularCommandDeg)
        
        # test
        while(flag is True):
            # robot wake up
            self.wakeUp()
            print("going to position : "+str(math.degrees(angularCommandRad))+" degrees")
            time.sleep(5)
            self.hipPitch.positionbloquant = (angularCommandRad, self.speed)
            time.sleep(3.0)
            self.closeBrakes()
            self.printRealInformations()
            jointsState = self.areJointStatics()
            flag = jointsState[0]
            if flag is True:
                print("success")
                print("\n")
                angularCommandRad += math.radians(self.increment)
            else:
                if(jointsState[1] is False and jointsState[2] is True):
                    print("Hip slip")
                    print("\n")
                if(jointsState[1] is True and jointsState[2] is False):
                    print("Knee slip")
                    print("\n")
                if(jointsState[1] is False and jointsState[2] is False):
                    print("Both joint sleep")
                    print("\n")
            if((abs(angularCommandRad) >= abs(self.hipPitch.mechanicalStopMax))):
                flag = False
                print("Impossible to go further, command out of mechanical stop")
        
        # out of the loop -> rest position
        print("Test finished, going to rest position")
        self.rest()
        
class CyclingWakeUpRestTest(MotionDynamicBrakesTest):
    def __init__(self, ip):
        self.ip = ip
        # proxy creation
        self.motion = ALProxy("ALMotion", self.ip, 9559)
        self.system = ALProxy("ALSystem", self.ip, 9559)
        # test parameters
        self.nbcyles = 10000
        # logger parameters
        self.testType = "brakes_cycling_wakeUp_rest"
        self.extension = "csv"
        self.date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.robotName = self.system.robotName()
        self.filePath = "-".join([self.robotName, self.date, self.testType])
        self.confFilePath = "multi_logger.cfg"
        self.samplePeriod = 0.02
        self.output = ".".join([self.filePath,self.extension])
        self.decimal = 3
        self.logger = multi_logger.Logger(self.ip, self.confFilePath, self.samplePeriod, self.output, self.decimal)
    
    def wakeUp(self):
        self.motion.wakeUp()
        
    def rest(self):
        self.motion.rest()
        
    def disableBrakesProtection(self):
        self.motion.setMotionConfig([["ENABLE_BRAKES_PROTECTION", False]])
        print("Brakes protection disabled")
        
    def enableBrakesProtection(self):
        self.motion.setMotionConfig([["ENABLE_BRAKES_PROTECTION", True]])
        print("Brakes protection enabled")
        
    def cycling_behavior(self):
        self.wakeUp()
        self.disableBrakesProtection()
        self.rest()
        self.enableBrakesProtection()
        time.sleep(5)
    
    def start(self):
        # start log
        self.logger.log()
        
        # cycling wakeUp-rest behavior
        for i in range(self.nbcyles):
            try:
                self.cycling_behavior()
                print(str(i+1))
            except KeyboardInterrupt:
                print("script finished, bye")
                exit()
        
        # stop log
        self.logger.stop()
        
            
# ---------------------------------        
# ------------- Main --------------
# ---------------------------------

def main(ip, jointName, direction, test, cyclingBrakingAngle, cycleNumber, initialAngle):
    if test == "Dynamic":
        test_brakes_motion_dynamic = MotionDynamicBrakesTest(ip, jointName, direction, cyclingBrakingAngle, cycleNumber)
        test_brakes_motion_dynamic.start()
    if test == "DynamicCycling":
        test_brakes_motion_dynamic = MotionDynamicBrakesTest(ip, jointName, direction, cyclingBrakingAngle, cycleNumber)
        test_brakes_motion_dynamic.startCycling()
    if test == "Static":
        test_brakes_motion_static = MotionStaticBrakesTest(ip, jointName, direction, initialAngle)
        test_brakes_motion_static.start()
    if test == "Cycling":
        test_wakeUp_rest = CyclingWakeUpRestTest(ip)
        test_wakeUp_rest.start()

# ---------------------------------        
# ----------- Parsing -------------
# ---------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1", help="Robot ip adress")
    parser.add_argument("--joint", type=str, default="HipPitch", help="Joint to test", choices=["HipPitch", "KneePitch"])
    parser.add_argument("--direction", type=str, default="Positive", help="Test direction", choices=["Positive", "Negative"])
    parser.add_argument("--test", type=str, default="Static", help="Test to be run", choices=["Static", "Dynamic", "DynamicCycling", "Cycling"])
    parser.add_argument("--cyclingBrakingAngle", type=float, default=10.0, help="Braking angle during cycling dynamic tests")
    parser.add_argument("--cycleNumber", type=int, default=1, help="Number of dynamic test cycles you want to do")
    parser.add_argument("--initialAngle", type=float, default=30.0, help="Braking initial angle (degrees)")
    
    args = parser.parse_args()
    
    main(args.ip, args.joint, args.direction, args.test, args.cyclingBrakingAngle, args.cycleNumber, args.initialAngle)