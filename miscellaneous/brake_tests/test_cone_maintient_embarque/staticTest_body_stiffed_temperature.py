#!/usr/bin/python

import sys
import os
import inspect
import time
import math
from hwdcmlib import *
from naoqi import ALProxy
import argparse

class Robot(object):
	"""This class describes the Robot"""
	def __init__(self, ip):
		self.ip = ip

		try:
			motion = ALProxy("ALMotion", ip, 9559)
			motion.exit()
		except RuntimeError:
			print "Motion already killed"

		self.dcm = ALProxy("DCM", ip, 9559)
		self.mem = ALProxy("ALMemory", ip, 9559)

	def setStiffness(self, joint, value):
		self.dcm.set(["Device/SubDeviceList/" + joint + "/Hardness/Actuator/Value", "Merge", [[float(value), self.dcm.getTime(0)]]])

	def setPosition(self, joint, value, goTime = 3, wait = False):
		self.dcm.set(["Device/SubDeviceList/" + joint + "/Position/Actuator/Value", "Merge", [[float(value), self.dcm.getTime(int(goTime) * 1000)]]])
		if wait:
			time.sleep(goTime + 1)

	def getPosition(self, joint):
		return self.mem.getData("Device/SubDeviceList/" + joint + "/Position/Sensor/Value")

	def getTemperature(self, joint):
		return self.mem.getData("Device/SubDeviceList/" + joint + "/Temperature/Sensor/Value")

	def wakeUp(self):
		DCMwakeUp(self.dcm)

	def rest(self):
		DCMrest(self.dcm)

	def areJointStatics(self, waitTime = 10, limitDeg = 0.5):
		initialPositionHip = self.getPosition("HipPitch")
		initialPositionHipDeg = math.degrees(initialPositionHip)

		initialPositionKnee = self.getPosition("KneePitch")
		initialPositionKneeDeg = math.degrees(initialPositionKnee)

		t0 = time.time()

		state = True
		hipStatic = True
		kneeStatic = True

		while time.time() - t0 <= waitTime and state is True:
			positionHip = self.getPosition("HipPitch")
			positionHipDeg = math.degrees(positionHip)

			positionKnee = self.getPosition("KneePitch")
			positionKneeDeg = math.degrees(positionKnee)

			diffHipDeg = abs(positionHipDeg - initialPositionHipDeg)
			if diffHipDeg > limitDeg:
				hipStatic = False

			diffKneeDeg = abs(positionKneeDeg - initialPositionKneeDeg)
			if diffKneeDeg > limitDeg:
				kneeStatic = False

			if (hipStatic, kneeStatic) == (False, True):
				state = "Hip slip"
			elif (hipStatic, kneeStatic) == (True, False):
				state = "Knee slip"
			elif (hipStatic, kneeStatic) == (False, False):
				state = "Both slip"

		return state


# MAIN

def main(robotIP, joint, direction, initialAngle, closeOneBrake):
	robot = Robot(robotIP)
	robot.wakeUp()
	
	if direction == "Positive":
		initialAngle = -initialAngle
	
	try:
		while True:
			print(" ".join([joint, direction, str(initialAngle), "deg"]))
	
			robot.setStiffness("HipPitch", 1.0)
			robot.setStiffness("KneePitch", 1.0)
	
			if joint == "HipPitch":
				robot.setPosition("HipPitch", math.radians(initialAngle), 1)
				robot.setPosition("KneePitch", 0., 1, True)
			else:
				robot.setPosition("HipPitch", 0., 1)
				robot.setPosition("KneePitch", math.radians(initialAngle), 1, True)
			
			if closeOneBrake == 0:
				robot.setStiffness("HipPitch", 0)
				robot.setStiffness("KneePitch", 0)
			if closeOneBrake == 1:
				if joint == "HipPitch":
					robot.setStiffness("HipPitch", 0)
				else:
					robot.setStiffness("KneePitch", 0)
			
			time.sleep(0.1)
			realAngle = robot.getPosition(joint)
			realAngleDegree = math.degrees(realAngle)
			
			print(" ".join(["Real joint angle =", str(round(realAngleDegree, 2)), "deg"]))
	
			state = robot.areJointStatics()
	
			if state is True:
				print(" ".join(["HipPitch Temperature =", str(robot.getTemperature("HipPitch"))]))
				print(" ".join(["KneePitch Temperature =", str(robot.getTemperature("KneePitch"))]))
				print("Success")
				print("")
			else:
				print(" ".join(["HipPitch Temperature =", str(robot.getTemperature("HipPitch"))]))
				print(" ".join(["KneePitch Temperature =", str(robot.getTemperature("KneePitch"))]))
				print(state)
				print("")
	
			if state is True:
				if direction == "Positive":
					initialAngle -= 1
				else:
					initialAngle += 1
			else:
				if direction == "Positive":
					initialAngle += 3
				else:
					initialAngle -= 3
	
	
	except KeyboardInterrupt:
		robot.wakeUp()
		robot.rest()
	
		
if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--ip", type=str, default="127.0.0.1", help="Robot ip adress")
	parser.add_argument("--joint", type=str, default="HipPitch", help="Joint to test", choices=["HipPitch", "KneePitch"])
	parser.add_argument("--direction", type=str, default="Positive", help="Test direction", choices=["Positive", "Negative"])
	parser.add_argument("--initialAngle", type=float, default=0.0, help="Initial Angle")
	parser.add_argument("--closeOneBrake", type=int, default=0, help="If = 1, it closes only the tested joint and keeps the stiffness on the other joint")
	
	args = parser.parse_args()
	
	main(args.ip, args.joint, args.direction, args.initialAngle, args.closeOneBrake)