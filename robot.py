# -*- coding: utf-8 -*-
"""
Created on Tue Nov 27 11:37:59 2018

@author: gparis
"""
###############################################################################
# imports
import robolink
from robolink import ITEM_TYPE_TARGET, ROBOTCOM_READY, RUNMODE_RUN_ROBOT  
from operator import sub  
from robodk import KUKA_2_Pose
import serial
import time
import re
import os
import glob
import sys
from shutil import copyfile
from shutil import move
import datetime
import tkinter as tk
import subprocess
import numpy as np
###############################################################################

###############################################################################
# 
# 
#
###############################################################################
class robotControl():
    
###############################################################################
    # no initialization necessary
    def __init__(self):
        pass
###############################################################################

###############################################################################
    # function to negate calls and buttons
    def doSomething(self):
        pass
###############################################################################

############################################################################### 
    # function to receive the vacuum monitoring status
    def vacuumMonitoring(self, pneumaticsSystem):
        
        # flush initial output
        pneumaticsSystem.flushInput()
        time.sleep(0.5)
        
        # send status request for the positioning table vaccum sensor
        # and read out if the vacuum is in tact or not 
        pneumaticsSystem.write(b'getin0\r')
        time.sleep(0.5)
        pneumaticsSystem.flush()
        vacPositioningTable = pneumaticsSystem.readline().decode('utf-8', 'ignore')
        
        # send status request for the robot gripper vaccum sensor
        # and read out if the vacuum is in tact or not 
        pneumaticsSystem.write(b'getin1\r')
        time.sleep(0.5)
        pneumaticsSystem.flush()
        vacRobotGripper = pneumaticsSystem.readline().decode('utf-8', 'ignore')
        
        return int(vacPositioningTable[-3]), int(vacRobotGripper[-3])
###############################################################################

###############################################################################
    # close the pneumatics system ports and 
    # the pneumatics system serial connection
    # close laserDESK and RoboDK
    # finish the log file
    # adjust the error log file
    # close python if necessary             
    def End(self, pneumaticsSystem, myObject, currentSlide, fid, Donor, finishedSlideString = [], inPython = 0):
        pneumaticsSystem.write(b'seta4:0\r')
        pneumaticsSystem.write(b'seta3:0\r')
        pneumaticsSystem.write(b'seta6:0\r')
        time.sleep(0.3)
        pneumaticsSystem.close()
        subprocess.Popen(["powershell.exe", '&"C:\SAT in Spots we Trust\FinalKill.ps1"'])
        if not finishedSlideString:
            for j in range(currentSlide, len(myObject.logFileRows)):
                 fid.write(myObject.logFileRows[j])
        else:
            fid.write(finishedSlideString)
            for j in range(currentSlide+1, len(myObject.logFileRows)):
                 fid.write(myObject.logFileRows[j])
        fid.close()
        fidError = open(r'../../log_error.txt', 'r')
        listOfStarters = fidError.readlines()
        listOfStarters[currentSlide] = Donor + '\n'
        fidError = open(r'../../log_error.txt', 'w')
        fidError.writelines(listOfStarters)
        fidError.close()
        if not inPython:
            sys.exit()
        else:
            os._exit(0)
###############################################################################
            
###############################################################################
    # close the pneumatics system ports and 
    # the pneumatics system serial connection
    # close laserDESK and RoboDK
    # finish the log file
    # adjust the error log file
    # close python if necessary             
    def EndDifferentModes(self, pneumaticsSystem, myObject, inPython = 0):
        pneumaticsSystem.write(b'seta4:0\r')
        pneumaticsSystem.write(b'seta3:0\r')
        pneumaticsSystem.write(b'seta6:0\r')
        time.sleep(0.3)
        pneumaticsSystem.close()
        subprocess.Popen(["powershell.exe", '&"C:\SAT in Spots we Trust\FinalKill.ps1"'])
        if not inPython:
            sys.exit()
        else:
            os._exit(0)
###############################################################################

###############################################################################
    # function to setup the synthesizer within RoboDK            
    def buildAutomation(self):
        
        # initialize RoboDK
        RL = robolink.Robolink(robodk_path="C:/Program Files/RoboDK/bin/RoboDK.exe")
        
        # Create a work station
        RL.AddStation('Automation')
        
        # Create the base robot frame
        # Add the robot to the station
        # Add the robot to the base robot frame
        robotFrame = RL.AddFrame('Robot Frame')
        robot = RL.AddFile('KUKA-KR-3-R540.robot')
        robot.setParent(robotFrame)
        
        # Delete the 'base' frame
        item = RL.Item('base')
        item.Delete()
        
        # Add the tool to the robot
        # Rotate the tool geometry to fit to reality
        # this needs to be measured
        tool = RL.AddFile('tool3_small.tool')        
        geometryRotX = 77.5
        geometryRotY = 0
        geometryRotZ = 0
        geometryRotA = 0
        geometryRotB = 90
        geometryRotC = -90 
        geometryRotationXYZABC = [geometryRotX, geometryRotY, geometryRotZ, 
                                  geometryRotA, geometryRotB, geometryRotC] 
        geometryRotationMat = KUKA_2_Pose(geometryRotationXYZABC)
        tool.setGeometryPose(geometryRotationMat)
        
        # Set the TCP
        # this needs to be measured
        toolOffsetX = 87.5
        toolOffsetY = 0
        toolOffsetZ = 104.5
        toolOffsetA = 0 
        toolOffsetB = 0
        toolOffsetC = 0
        toolOffsetXYZABC = [toolOffsetX, toolOffsetY, toolOffsetZ, 
                            toolOffsetA, toolOffsetB, toolOffsetC] 
        toolOffsetMat = KUKA_2_Pose(toolOffsetXYZABC)
        tool.setPoseTool(toolOffsetMat)
        
        # Add the plate frame 
        # Add the plate frame to the robot frame
        # shift and rotate the frame
        # this needs to be measured
        framePlate = RL.AddFrame('slideHolder')
        framePlateX = 250
        framePlateY = 287.5
        framePlateZ = 11.6
        framePlateA = 0
        framePlateB = 0
        framePlateC = 0
        framePlate.setParent(robotFrame)
        framePlateXYZABC = [framePlateX, framePlateY, framePlateZ, 
                            framePlateA, framePlateB, framePlateC]
        framePlateMat = KUKA_2_Pose(framePlateXYZABC)
        framePlate.setPose(framePlateMat)
        
        # Add the plate
        # Add the plate to the plate frame
        # shift the plate to the right location
        # this needs to be measured
        plate = RL.AddFile('slideHolder.stl')
        plateX = 0 
        plateY = 0 
        plateZ = -11.6
        plateA = 0
        plateB = 0
        plateC = 0
        plate.setParent(framePlate)
        plateXYZABC = [plateX, plateY, plateZ,
                        plateA, plateB, plateC] 
        plateMat = KUKA_2_Pose(plateXYZABC)
        plate.setPose(plateMat)
        
        # Add the dummy frame 
        # Add the dummy frame to the robot frame
        # shift the frame to the right location
        # this needs to be measured
        frameDummy = RL.AddFrame('dummy')
        frameDummyX = 713.1
        frameDummyY = -85
        frameDummyZ = 0
        frameDummyA = -90
        frameDummyB = 0
        frameDummyC = 0
        frameDummy.setParent(robotFrame)
        frameDummyXYZABC = [frameDummyX, frameDummyY, frameDummyZ, 
                            frameDummyA, frameDummyB, frameDummyC] 
        frameDummyMat = KUKA_2_Pose(frameDummyXYZABC)
        frameDummy.setPose(frameDummyMat)
        
        # Add the plate
        # Add the plate to the plate frame
        # shift the plate to the right location
        # this needs to be measured
        dummy = RL.AddFile('dummy_system2.stl')
        dummyX = 0
        dummyY = 0
        dummyZ = 407
        dummyA = 180
        dummyB = 0
        dummyC = 90
        dummy.setParent(frameDummy)
        dummyXYZABC = [dummyX, dummyY, dummyZ,
                       dummyA, dummyB, dummyC] 
        dummyMat = KUKA_2_Pose(dummyXYZABC)
        dummy.setPose(dummyMat)
        
        # number of positions in x and y direction within the slide holder
        # midpoint-to-midpoint distance between positions in x and y direction
        # define the first pick up location, including real world tolerances
        # define the pick up safe distance for all positions (height)
        # define the pick up safe distance for the drop off location
        # define the slide thickness
        slidesX = 9
        slidesY = 3
        dxSlides = 35.6
        dySlides = 89.6
        zFramePlateOffset = -4.55 
        firstPickUpRotA = 0
        firstPickUpRotB = 90
        firstPickUpRotC = 0
        finalToolRotA = -2.25 
        finalToolRotB = 90
        finalToolRotC = 0
        firstPickUp = [4*dxSlides + 2.9, dySlides - 2.0, 0, 
                       firstPickUpRotA, firstPickUpRotB, firstPickUpRotC] 
        pickUpSafeDistance = 20
        dropOffX = 416.5
        dropOffY = -378 
        dropOffZ = 149
        dropOffXSafeDistance = 150
        dropOffZSafeDistance = 31
        slideThickness = 1
        
        # Add the home target
        RL.AddTarget('home', framePlate)
        
        # Add the slide holder pick up targets including real wordl tolerances
        for i in range(slidesX):
            for j in range(slidesY):
                if(j == 2 and i == 0):
                    pickUpIJ = RL.AddTarget('Pick up' + str(i+1) + str(j+1), framePlate)
                    pickUpIJSafe = RL.AddTarget('Pick up safe' + str(i) + str(j), framePlate)
                    pickUpIJXYZABC = map(sub, firstPickUp, [i*dxSlides + 1.0, j*dySlides - 0.95, zFramePlateOffset, 0, 0, 0])
                    pickUpIJSafeXYZABC = map(sub, firstPickUp, [i*dxSlides + 1.0, j*dySlides - 0.95, zFramePlateOffset - pickUpSafeDistance, 0, 0, 0])
                    pickUpIJMat = KUKA_2_Pose(pickUpIJXYZABC)
                    pickUpIJSafeMat = KUKA_2_Pose(pickUpIJSafeXYZABC)
                    pickUpIJ.setPose(pickUpIJMat)
                    pickUpIJSafe.setPose(pickUpIJSafeMat)
                elif(j == 2 and i == 1):
                    pickUpIJ = RL.AddTarget('Pick up' + str(i+1) + str(j+1), framePlate)
                    pickUpIJSafe = RL.AddTarget('Pick up safe' + str(i) + str(j), framePlate)
                    pickUpIJXYZABC = map(sub, firstPickUp, [i*dxSlides + 1.0, j*dySlides - 0.75, zFramePlateOffset, 0, 0, 0])
                    pickUpIJSafeXYZABC = map(sub, firstPickUp, [i*dxSlides + 1.0, j*dySlides - 0.75, zFramePlateOffset - pickUpSafeDistance, 0, 0, 0])
                    pickUpIJMat = KUKA_2_Pose(pickUpIJXYZABC)
                    pickUpIJSafeMat = KUKA_2_Pose(pickUpIJSafeXYZABC)
                    pickUpIJ.setPose(pickUpIJMat)
                    pickUpIJSafe.setPose(pickUpIJSafeMat)                    
                elif(j == 2 and i == 2):                    
                    pickUpIJ = RL.AddTarget('Pick up' + str(i+1) + str(j+1), framePlate)
                    pickUpIJSafe = RL.AddTarget('Pick up safe' + str(i) + str(j), framePlate)
                    pickUpIJXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.75, j*dySlides - 0.75, zFramePlateOffset, 0, 0, 0])
                    pickUpIJSafeXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.75, j*dySlides - 0.75, zFramePlateOffset - pickUpSafeDistance, 0, 0, 0])
                    pickUpIJMat = KUKA_2_Pose(pickUpIJXYZABC)
                    pickUpIJSafeMat = KUKA_2_Pose(pickUpIJSafeXYZABC)
                    pickUpIJ.setPose(pickUpIJMat)
                    pickUpIJSafe.setPose(pickUpIJSafeMat)                    
                elif(j == 2 and i >= 3 and i < 4):                    
                    pickUpIJ = RL.AddTarget('Pick up' + str(i+1) + str(j+1), framePlate)
                    pickUpIJSafe = RL.AddTarget('Pick up safe' + str(i) + str(j), framePlate)
                    pickUpIJXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.5, j*dySlides - 0.75, zFramePlateOffset, 0, 0, 0])
                    pickUpIJSafeXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.5, j*dySlides - 0.75, zFramePlateOffset - pickUpSafeDistance, 0, 0, 0])
                    pickUpIJMat = KUKA_2_Pose(pickUpIJXYZABC)
                    pickUpIJSafeMat = KUKA_2_Pose(pickUpIJSafeXYZABC)
                    pickUpIJ.setPose(pickUpIJMat)
                    pickUpIJSafe.setPose(pickUpIJSafeMat)                    
                elif(j == 2 and i == 4):                    
                    pickUpIJ = RL.AddTarget('Pick up' + str(i+1) + str(j+1), framePlate)
                    pickUpIJSafe = RL.AddTarget('Pick up safe' + str(i) + str(j), framePlate)
                    pickUpIJXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.5, j*dySlides - 1.0, zFramePlateOffset, 0, 0, 0])
                    pickUpIJSafeXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.5, j*dySlides - 1.0, zFramePlateOffset - pickUpSafeDistance, 0, 0, 0])
                    pickUpIJMat = KUKA_2_Pose(pickUpIJXYZABC)
                    pickUpIJSafeMat = KUKA_2_Pose(pickUpIJSafeXYZABC)
                    pickUpIJ.setPose(pickUpIJMat)
                    pickUpIJSafe.setPose(pickUpIJSafeMat)                    
                elif(j == 2 and i == 5):                    
                    pickUpIJ = RL.AddTarget('Pick up' + str(i+1) + str(j+1), framePlate)
                    pickUpIJSafe = RL.AddTarget('Pick up safe' + str(i) + str(j), framePlate)
                    pickUpIJXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.5, j*dySlides - 1.25, zFramePlateOffset, 0, 0, 0])
                    pickUpIJSafeXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.5, j*dySlides - 1.25, zFramePlateOffset - pickUpSafeDistance, 0, 0, 0])
                    pickUpIJMat = KUKA_2_Pose(pickUpIJXYZABC)
                    pickUpIJSafeMat = KUKA_2_Pose(pickUpIJSafeXYZABC)
                    pickUpIJ.setPose(pickUpIJMat)
                    pickUpIJSafe.setPose(pickUpIJSafeMat)                
                elif(j == 2 and i == 6):                    
                    pickUpIJ = RL.AddTarget('Pick up' + str(i+1) + str(j+1), framePlate)
                    pickUpIJSafe = RL.AddTarget('Pick up safe' + str(i) + str(j), framePlate)
                    pickUpIJXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.5, j*dySlides - 1.5, zFramePlateOffset, 0, 0, 0])
                    pickUpIJSafeXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.5, j*dySlides - 1.5, zFramePlateOffset - pickUpSafeDistance, 0, 0, 0])
                    pickUpIJMat = KUKA_2_Pose(pickUpIJXYZABC)
                    pickUpIJSafeMat = KUKA_2_Pose(pickUpIJSafeXYZABC)
                    pickUpIJ.setPose(pickUpIJMat)
                    pickUpIJSafe.setPose(pickUpIJSafeMat)                    
                elif(j == 2 and i == 7):                    
                    pickUpIJ = RL.AddTarget('Pick up' + str(i+1) + str(j+1), framePlate)
                    pickUpIJSafe = RL.AddTarget('Pick up safe' + str(i) + str(j), framePlate)
                    pickUpIJXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.5, j*dySlides - 1.75, zFramePlateOffset, 0, 0, 0])
                    pickUpIJSafeXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.5, j*dySlides - 1.75, zFramePlateOffset - pickUpSafeDistance, 0, 0, 0])
                    pickUpIJMat = KUKA_2_Pose(pickUpIJXYZABC)
                    pickUpIJSafeMat = KUKA_2_Pose(pickUpIJSafeXYZABC)
                    pickUpIJ.setPose(pickUpIJMat)
                    pickUpIJSafe.setPose(pickUpIJSafeMat)                    
                elif(j == 2 and i == 8):                    
                    pickUpIJ = RL.AddTarget('Pick up' + str(i+1) + str(j+1), framePlate)
                    pickUpIJSafe = RL.AddTarget('Pick up safe' + str(i) + str(j), framePlate)
                    pickUpIJXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.25, j*dySlides - 1.75, zFramePlateOffset, 0, 0, 0])
                    pickUpIJSafeXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.25, j*dySlides - 1.75, zFramePlateOffset - pickUpSafeDistance, 0, 0, 0])
                    pickUpIJMat = KUKA_2_Pose(pickUpIJXYZABC)
                    pickUpIJSafeMat = KUKA_2_Pose(pickUpIJSafeXYZABC)
                    pickUpIJ.setPose(pickUpIJMat)
                    pickUpIJSafe.setPose(pickUpIJSafeMat)                
                elif(j == 1 and i == 2):                    
                    pickUpIJ = RL.AddTarget('Pick up' + str(i+1) + str(j+1), framePlate)
                    pickUpIJSafe = RL.AddTarget('Pick up safe' + str(i) + str(j), framePlate)
                    pickUpIJXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.5, j*dySlides - 0.5, zFramePlateOffset, 0, 0, 0])
                    pickUpIJSafeXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.5, j*dySlides - 0.5, zFramePlateOffset - pickUpSafeDistance, 0, 0, 0])
                    pickUpIJMat = KUKA_2_Pose(pickUpIJXYZABC)
                    pickUpIJSafeMat = KUKA_2_Pose(pickUpIJSafeXYZABC)
                    pickUpIJ.setPose(pickUpIJMat)
                    pickUpIJSafe.setPose(pickUpIJSafeMat)                    
                elif(j == 1 and i == 3):                   
                    pickUpIJ = RL.AddTarget('Pick up' + str(i+1) + str(j+1), framePlate)
                    pickUpIJSafe = RL.AddTarget('Pick up safe' + str(i) + str(j), framePlate)
                    pickUpIJXYZABC = map(sub, firstPickUp, [i*dxSlides+0.5, j*dySlides-0.75, zFramePlateOffset, 0, 0, 0])
                    pickUpIJSafeXYZABC = map(sub, firstPickUp, [i*dxSlides+0.5, j*dySlides-0.75, zFramePlateOffset - pickUpSafeDistance, 0, 0, 0])
                    pickUpIJMat = KUKA_2_Pose(pickUpIJXYZABC)
                    pickUpIJSafeMat = KUKA_2_Pose(pickUpIJSafeXYZABC)
                    pickUpIJ.setPose(pickUpIJMat)
                    pickUpIJSafe.setPose(pickUpIJSafeMat)                    
                elif(j == 1 and i == 4):                    
                    pickUpIJ = RL.AddTarget('Pick up' + str(i+1) + str(j+1), framePlate)
                    pickUpIJSafe = RL.AddTarget('Pick up safe' + str(i) + str(j), framePlate)
                    pickUpIJXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.5, j*dySlides - 1.0, zFramePlateOffset, 0, 0, 0])
                    pickUpIJSafeXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.5, j*dySlides - 1.0, zFramePlateOffset - pickUpSafeDistance, 0, 0, 0])
                    pickUpIJMat = KUKA_2_Pose(pickUpIJXYZABC)
                    pickUpIJSafeMat = KUKA_2_Pose(pickUpIJSafeXYZABC)
                    pickUpIJ.setPose(pickUpIJMat)
                    pickUpIJSafe.setPose(pickUpIJSafeMat)                    
                elif(j == 1 and i == 5):                    
                    pickUpIJ = RL.AddTarget('Pick up' + str(i+1) + str(j+1), framePlate)
                    pickUpIJSafe = RL.AddTarget('Pick up safe' + str(i) + str(j), framePlate)
                    pickUpIJXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.25, j*dySlides - 1.25, zFramePlateOffset, 0, 0, 0])
                    pickUpIJSafeXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.25, j*dySlides - 1.25, zFramePlateOffset - pickUpSafeDistance, 0, 0, 0])
                    pickUpIJMat = KUKA_2_Pose(pickUpIJXYZABC)
                    pickUpIJSafeMat = KUKA_2_Pose(pickUpIJSafeXYZABC)
                    pickUpIJ.setPose(pickUpIJMat)
                    pickUpIJSafe.setPose(pickUpIJSafeMat)                
                elif(j == 1 and i == 6):                    
                    pickUpIJ = RL.AddTarget('Pick up' + str(i+1) + str(j+1), framePlate)
                    pickUpIJSafe = RL.AddTarget('Pick up safe' + str(i) + str(j), framePlate)
                    pickUpIJXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.5, j*dySlides-1.5, zFramePlateOffset, 0, 0, 0])
                    pickUpIJSafeXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.5, j*dySlides-1.5, zFramePlateOffset - pickUpSafeDistance, 0, 0, 0])
                    pickUpIJMat = KUKA_2_Pose(pickUpIJXYZABC)
                    pickUpIJSafeMat = KUKA_2_Pose(pickUpIJSafeXYZABC)
                    pickUpIJ.setPose(pickUpIJMat)
                    pickUpIJSafe.setPose(pickUpIJSafeMat)                   
                elif(j == 1 and i == 7):                    
                    pickUpIJ = RL.AddTarget('Pick up' + str(i+1) + str(j+1), framePlate)
                    pickUpIJSafe = RL.AddTarget('Pick up safe' + str(i) + str(j), framePlate)
                    pickUpIJXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.25, j*dySlides - 1.75, zFramePlateOffset, 0, 0, 0])
                    pickUpIJSafeXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.25, j*dySlides - 1.75, zFramePlateOffset - pickUpSafeDistance, 0, 0, 0])
                    pickUpIJMat = KUKA_2_Pose(pickUpIJXYZABC)
                    pickUpIJSafeMat = KUKA_2_Pose(pickUpIJSafeXYZABC)
                    pickUpIJ.setPose(pickUpIJMat)
                    pickUpIJSafe.setPose(pickUpIJSafeMat)                   
                elif(j == 1 and i == 8):                   
                    pickUpIJ = RL.AddTarget('Pick up' + str(i+1) + str(j+1), framePlate)
                    pickUpIJSafe = RL.AddTarget('Pick up safe' + str(i) + str(j), framePlate)
                    pickUpIJXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.5, j*dySlides - 1.5, zFramePlateOffset, 0, 0, 0])
                    pickUpIJSafeXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.5, j*dySlides - 1.5, zFramePlateOffset - pickUpSafeDistance, 0, 0, 0])
                    pickUpIJMat = KUKA_2_Pose(pickUpIJXYZABC)
                    pickUpIJSafeMat = KUKA_2_Pose(pickUpIJSafeXYZABC)
                    pickUpIJ.setPose(pickUpIJMat)
                    pickUpIJSafe.setPose(pickUpIJSafeMat)                    
                elif(j == 0 and i == 3):                    
                    pickUpIJ = RL.AddTarget('Pick up' + str(i+1) + str(j+1), framePlate)
                    pickUpIJSafe = RL.AddTarget('Pick up safe' + str(i) + str(j), framePlate)
                    pickUpIJXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.5, j*dySlides - 0.5, zFramePlateOffset, 0, 0, 0])
                    pickUpIJSafeXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.5, j*dySlides - 0.5, zFramePlateOffset - pickUpSafeDistance, 0, 0, 0])
                    pickUpIJMat = KUKA_2_Pose(pickUpIJXYZABC)
                    pickUpIJSafeMat = KUKA_2_Pose(pickUpIJSafeXYZABC)
                    pickUpIJ.setPose(pickUpIJMat)
                    pickUpIJSafe.setPose(pickUpIJSafeMat)
                elif(j == 0 and i == 4):                    
                    pickUpIJ = RL.AddTarget('Pick up' + str(i+1) + str(j+1), framePlate)
                    pickUpIJSafe = RL.AddTarget('Pick up safe' + str(i) + str(j), framePlate)
                    pickUpIJXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.5, j*dySlides - 0.75, zFramePlateOffset, 0, 0, 0])
                    pickUpIJSafeXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.5, j*dySlides - 0.75, zFramePlateOffset - pickUpSafeDistance, 0, 0, 0])
                    pickUpIJMat = KUKA_2_Pose(pickUpIJXYZABC)
                    pickUpIJSafeMat = KUKA_2_Pose(pickUpIJSafeXYZABC)
                    pickUpIJ.setPose(pickUpIJMat)
                    pickUpIJSafe.setPose(pickUpIJSafeMat)                    
                elif(j == 0 and i == 5):                   
                    pickUpIJ = RL.AddTarget('Pick up' + str(i+1) + str(j+1), framePlate)
                    pickUpIJSafe = RL.AddTarget('Pick up safe' + str(i) + str(j), framePlate)
                    pickUpIJXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.25, j*dySlides - 1.0, zFramePlateOffset, 0, 0, 0])
                    pickUpIJSafeXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.25, j*dySlides - 1.0, zFramePlateOffset - pickUpSafeDistance, 0, 0, 0])
                    pickUpIJMat = KUKA_2_Pose(pickUpIJXYZABC)
                    pickUpIJSafeMat = KUKA_2_Pose(pickUpIJSafeXYZABC)
                    pickUpIJ.setPose(pickUpIJMat)
                    pickUpIJSafe.setPose(pickUpIJSafeMat)                    
                elif(j == 0 and i == 6):                    
                    pickUpIJ = RL.AddTarget('Pick up' + str(i+1) + str(j+1), framePlate)
                    pickUpIJSafe = RL.AddTarget('Pick up safe' + str(i) + str(j), framePlate)
                    pickUpIJXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.5, j*dySlides - 1.0, zFramePlateOffset, 0, 0, 0])
                    pickUpIJSafeXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.5, j*dySlides - 1.0, zFramePlateOffset - pickUpSafeDistance, 0, 0, 0])
                    pickUpIJMat = KUKA_2_Pose(pickUpIJXYZABC)
                    pickUpIJSafeMat = KUKA_2_Pose(pickUpIJSafeXYZABC)
                    pickUpIJ.setPose(pickUpIJMat)
                    pickUpIJSafe.setPose(pickUpIJSafeMat)                   
                elif(j == 0 and i == 7):                    
                    pickUpIJ = RL.AddTarget('Pick up' + str(i+1) + str(j+1), framePlate)
                    pickUpIJSafe = RL.AddTarget('Pick up safe' + str(i) + str(j), framePlate)
                    pickUpIJXYZABC = map(sub, firstPickUp, [i*dxSlides, j*dySlides - 1.25, zFramePlateOffset, 0, 0, 0])
                    pickUpIJSafeXYZABC = map(sub, firstPickUp, [i*dxSlides, j*dySlides - 1.25, zFramePlateOffset - pickUpSafeDistance, 0, 0, 0])
                    pickUpIJMat = KUKA_2_Pose(pickUpIJXYZABC)
                    pickUpIJSafeMat = KUKA_2_Pose(pickUpIJSafeXYZABC)
                    pickUpIJ.setPose(pickUpIJMat)
                    pickUpIJSafe.setPose(pickUpIJSafeMat)                   
                elif(j == 0 and i == 8):                  
                    pickUpIJ = RL.AddTarget('Pick up' + str(i+1) + str(j+1), framePlate)
                    pickUpIJSafe = RL.AddTarget('Pick up safe' + str(i) + str(j), framePlate)
                    pickUpIJXYZABC = map(sub, firstPickUp, [i*dxSlides, j*dySlides-1.25, zFramePlateOffset, 0, 0, 0])
                    pickUpIJSafeXYZABC = map(sub, firstPickUp, [i*dxSlides, j*dySlides-1.25, zFramePlateOffset - pickUpSafeDistance, 0, 0, 0])
                    pickUpIJMat = KUKA_2_Pose(pickUpIJXYZABC)
                    pickUpIJSafeMat = KUKA_2_Pose(pickUpIJSafeXYZABC)
                    pickUpIJ.setPose(pickUpIJMat)
                    pickUpIJSafe.setPose(pickUpIJSafeMat)                 
                else:               
                    pickUpIJ = RL.AddTarget('Pick up' + str(i+1) + str(j+1), framePlate)
                    pickUpIJSafe = RL.AddTarget('Pick up safe' + str(i) + str(j), framePlate)
                    pickUpIJXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.5, j*dySlides, zFramePlateOffset, 0, 0, 0])
                    pickUpIJSafeXYZABC = map(sub, firstPickUp, [i*dxSlides + 0.5, j*dySlides, zFramePlateOffset - pickUpSafeDistance, 0, 0, 0])
                    pickUpIJMat = KUKA_2_Pose(pickUpIJXYZABC)
                    pickUpIJSafeMat = KUKA_2_Pose(pickUpIJSafeXYZABC)
                    pickUpIJ.setPose(pickUpIJMat)
                    pickUpIJSafe.setPose(pickUpIJSafeMat)
        
        # Add the pre drop off location 
        preDropOffLocation1 = RL.AddTarget('Pre-drop off location 1', framePlate)
        preDropOffLocationXYZABC1 = [dropOffX - dropOffXSafeDistance, dropOffY, dropOffZ + dropOffZSafeDistance, finalToolRotA, finalToolRotB, finalToolRotC]
        preDropOffLocationMat1 = KUKA_2_Pose(preDropOffLocationXYZABC1)
        preDropOffLocation1.setPose(preDropOffLocationMat1)
        
        preDropOffLocation2 = RL.AddTarget('Pre-drop off location 2', framePlate)
        preDropOffLocationXYZABC2 = [dropOffX, dropOffY, dropOffZ + dropOffZSafeDistance, finalToolRotA, finalToolRotB, finalToolRotC]
        preDropOffLocationMat2 = KUKA_2_Pose(preDropOffLocationXYZABC2)
        preDropOffLocation2.setPose(preDropOffLocationMat2)
        
        # Add the drop off locations
        # Add drop location 1
        dropOffLocation1 = RL.AddTarget('Drop off location 1', framePlate)
        dropOffLocationXYZABC = [dropOffX, dropOffY, dropOffZ, finalToolRotA, finalToolRotB, finalToolRotC - 1]
        dropOffLocationMat1 = KUKA_2_Pose(dropOffLocationXYZABC)
        dropOffLocation1.setPose(dropOffLocationMat1)
        
        # Add drop location 2
        dropOffLocation2 = RL.AddTarget('Drop off location 2', framePlate)
        dropOffLocationXYZABC2 = [dropOffX - 2.0, dropOffY - 1.1, dropOffZ + slideThickness + 0.35, finalToolRotA, finalToolRotB, finalToolRotC - 2.4] 
        dropOffLocationMat2 = KUKA_2_Pose(dropOffLocationXYZABC2)
        dropOffLocation2.setPose(dropOffLocationMat2)
        
        # Add drop location pick up location 1
        dropOffPickUpLocation1 = RL.AddTarget('Drop off pick up location 1', framePlate)
        dropOffPickUpLocationXYZABC1 = [dropOffX - 2.95, dropOffY - 0.6, dropOffZ - 1.1, finalToolRotA, finalToolRotB, finalToolRotC - 2.075]
        dropOffPickUpLocationMat1 = KUKA_2_Pose(dropOffPickUpLocationXYZABC1)
        dropOffPickUpLocation1.setPose(dropOffPickUpLocationMat1)
        
        # Add wait location
        waitLocation = RL.AddTarget('Wait location', framePlate)
        waitLocationXYZABC = [dropOffX - 2.0, dropOffY - 1.1, dropOffZ + slideThickness + 2.35, finalToolRotA, finalToolRotB, finalToolRotC - 2.4] 
        waitLocationMat = KUKA_2_Pose(waitLocationXYZABC)
        waitLocation.setPose(waitLocationMat)
###############################################################################

###############################################################################        
    def run(self, myObject, laserObject):
           
        # generate log file back up and move the old one into the archive
        currentTime = datetime.datetime.now()
        logString = 'log_back_' + re.sub(r":", r"_", str(currentTime)) + '.txt'
        logfiles = glob.glob("log_back_*")
        if not logfiles:
            pass
        else:
            move(logfiles[0], r'logfileArchive/' + logfiles[0])
        copyfile('log.txt', logString)
        
        # define the AA positions
        aminoacids = {
               'A':4,
               'C':5,
               'D':6,
               'E':7,
               'F':8,
               'G':9,
               'H':10,
               'I':11,
               'K':12,
               'L':13,
               'M':14,
               'N':15,
               'P':16,
               'Q':17,
               'R':18,
               'S':19,
               'T':20,
               'V':21,
               'W':22,
               'Y':23,
               'B':24,
               'J':25,
               'Z':26
               }
        revAminoacids = {v: k for k, v in aminoacids.items()}
        
        # set up a connection with the pneumatics system
        pneumaticsSystem = serial.Serial('COM6', 57600, timeout=1)
        if(not(pneumaticsSystem.isOpen())):
            pneumaticsSystem.open()
        time.sleep(0.5)
        
        # get an instance of the opend RoboDK software
        RL = robolink.Robolink()
        
        # get the target coordinates
        robot = RL.Item('KUKA KR 3 R540')
        targets = RL.ItemList(ITEM_TYPE_TARGET)
        home = targets[0]
        preDropOffLocation = targets[-6:-4]
        dropOffLocation = targets[-4:-1]
        waitLocation = [targets[-1]]
        notPickUp = len(preDropOffLocation) + len(dropOffLocation) + len(waitLocation)
        pickUpLocation = targets[1:len(targets)-notPickUp:2]
        safePickUpLocation = targets[2:len(targets)-notPickUp:2]
        
        # connect to the robot
        RUN_ON_ROBOT = True
        checkValue = 1        
        robot.setConnectionParams('172.31.1.147', 7000, '/', 'anonymous','')
        while(checkValue):
            try:
                if RUN_ON_ROBOT:
                    # Connect to the robot using default connetion parameters
                    robot.Connect()
                    status, status_msg = robot.ConnectedState()
                    if status != ROBOTCOM_READY:
                        # Stop if the connection did not succeed
                        print(status_msg)
                        raise Exception("Failed to connect: " + status_msg)  
                    # Set to run the robot commands on the robot
                    RL.setRunMode(RUNMODE_RUN_ROBOT)
                    # Note: This is set automatically if we use
                    # robot.Connect() through the API
                checkValue = 0
            except:
                time.sleep(1)
                pass
        
        # move to the home target -> savety        
        robot.MoveJ(home)
        
        # prepare the upload folder for the sld files
        try:
            if(os.path.isfile('C:\Transfer\Transfer.sld')):
                os.remove('C:\Transfer\Transfer.sld')
        except:
            pass
        try:        
            if(os.path.isfile('C:\Transfer\Transfer1.sld')):
                os.remove('C:\Transfer\Transfer1.sld')
        except:
            pass                   
        if(os.path.isfile('C:\Transfer\Transfer.sld')):
            fileChange = False
        else:
            fileChange = True
        
        # open the log file
        fid = open(r'log.txt', 'w')
        
        # transportation procedure
        numberOfSlide = len(myObject.logFileLayer.slideState)
        for i in range(numberOfSlide):

            # acceptor slide transportation and positioning
            if(myObject.logFileLayer.slideState[i]):
                robot.MoveJ(safePickUpLocation[i])
                robot.MoveJ(pickUpLocation[i])
                pneumaticsSystem.write(b'seta4:1\r')
                time.sleep(3.0)
                robot.MoveJ(safePickUpLocation[i])
                robot.MoveJ(preDropOffLocation[0])
                robot.MoveJ(preDropOffLocation[1])
                pneumaticsSystem.write(b'seta6:1\r')
                time.sleep(1)
                robot.MoveJ(dropOffLocation[0])
                pneumaticsSystem.write(b'seta4:0\r')
                time.sleep(1.0)
                pneumaticsSystem.write(b'seta5:1\r')
                time.sleep(5)
                robot.MoveJ(preDropOffLocation[1])
                pneumaticsSystem.write(b'seta5:0\r')
                robot.MoveJ(preDropOffLocation[0])
                pneumaticsSystem.write(b'seta1:1\r')
                pneumaticsSystem.write(b'seta0:1\r')
                time.sleep(5)
                pneumaticsSystem.write(b'seta1:0\r')
                pneumaticsSystem.write(b'seta0:0\r')
                pneumaticsSystem.write(b'seta2:1\r')
                time.sleep(5)
                pneumaticsSystem.write(b'seta2:0\r')
                pneumaticsSystem.write(b'seta1:1\r')
                pneumaticsSystem.write(b'seta0:1\r')
                time.sleep(5)
                pneumaticsSystem.write(b'seta2:1\r')
                time.sleep(5)
                pneumaticsSystem.write(b'seta1:0\r')
                pneumaticsSystem.write(b'seta0:0\r')
                pneumaticsSystem.write(b'seta2:0\r')
                pneumaticsSystem.write(b'seta3:1\r')
                
                # laser transfer file generation
                logString = myObject.generateJobFiles(ActiveSlideState = i) 
                idx = [m.start() for m in re.finditer('\t', myObject.logFileRows[i])]
                layer_number = int(myObject.logFileRows[i][idx[1]+2:idx[1]+2+2]) + myObject.logFileLayer.nextLayer[i]
                os.chdir(myObject.logFileRows[i][:idx[0]])
                os.chdir('L%02i' % layer_number)
                
                # get the list of AA files -> transfer files
                tmpList = []
                for x in myObject.filenames:
                    tmpList.append(x[3])
                AAList = list(map(aminoacids.get, tmpList))
                
                # donor slide transportation and positioning
                for fileIdx, j in enumerate(AAList):
                    
                    robot.MoveJ(safePickUpLocation[j])
                    robot.MoveJ(pickUpLocation[j])
                    pneumaticsSystem.write(b'seta4:1\r')
                    time.sleep(3.0)
                    robot.MoveJ(safePickUpLocation[j])
                    
                    # check vacuum sensors for malfunction
                    vac1, vac2 = self.vacuumMonitoring(pneumaticsSystem)
                    if not(vac1 and vac2):
                        subprocess.Popen(["powershell.exe", '&"C:\SAT in Spots we Trust\Error.ps1"'])
                        ErrorVac1 = tk.Tk()
                        ErrorVac1.geometry("400x85")
                        ErrorVac1.attributes("-topmost", True)
                        ErrorVac1.protocol('WM_DELETE_WINDOW', self.doSomething)
                        ErrorVac1Msg = tk.Label(ErrorVac1, text='A malfunction occured. Please get someone to fix it!')
                        ErrorVac1Msg.pack()
                        EndButton1 = tk.Button(ErrorVac1, text="Exit", command = lambda: self.End(pneumaticsSystem, myObject, i, fid, revAminoacids[j]))
                        EndButton1.pack()
                        continueButton1 = tk.Button(ErrorVac1, text="Continue", command = ErrorVac1.destroy)
                        continueButton1.pack()
                        ErrorVac1.mainloop()
                    
                    robot.MoveJ(preDropOffLocation[0])
                    robot.MoveJ(preDropOffLocation[1])
                    time.sleep(1)
                    robot.MoveJ(dropOffLocation[1])
                    pneumaticsSystem.write(b'seta4:0\r')
                    time.sleep(1.0)
                    pneumaticsSystem.write(b'seta5:1\r')
                    time.sleep(2.5)
                    robot.MoveJ(preDropOffLocation[1])
                    pneumaticsSystem.write(b'seta5:0\r')
                    robot.MoveJ(preDropOffLocation[0])
                    
                    # upload the transfer file to laserDESK and wait for a response
                    laserObject.uploadJobFile(myObject.filenames[fileIdx], fileChange)
                    statusLaser = ''
                    time.sleep(1.5)
                    while(not("b'\\x02\\x08\\x00\\x00\\x00\\x04\\x00\\x00\\x00\\x1f\\xa3\\x01\\x00\\t\\x03'" == statusLaser)):
                        time.sleep(1)
                        statusLaser = laserObject.status()
                    if(fileChange):
                        if(os.path.isfile('C:\Transfer\Transfer1.sld')):
                            os.remove('C:\Transfer\Transfer1.sld')
                    else:
                        if(os.path.isfile('C:\Transfer\Transfer.sld')):
                            os.remove('C:\Transfer\Transfer.sld')
                            
                    # transfer the file x-times according to the user input
                    for q in range(int(myObject.repeatLasing[j-4])):  
                        laserObject.laserOn()
                        statusLaser = ''
                        time.sleep(1.5)
                        while(not("b'\\x02\\x08\\x00\\x00\\x00\\x04\\x00\\x00\\x00\\x1f\\xa3\\x01\\x00\\t\\x03'" == statusLaser)):
                            time.sleep(1)
                            statusLaser = laserObject.status()
                                                   
                    robot.MoveJ(preDropOffLocation[1])
                    time.sleep(1)
                    robot.MoveJ(dropOffLocation[1])
                    pneumaticsSystem.write(b'seta4:1\r')                    
                    time.sleep(5.0) 
                    robot.MoveJ(waitLocation[0])
                    time.sleep(2.0)                 
                    robot.MoveJ(preDropOffLocation[1])
                    robot.MoveJ(preDropOffLocation[0])
                    
                    # check vacuum sensors for malfunction
                    vac1, vac2 = self.vacuumMonitoring(pneumaticsSystem)
                    if not(vac1 and vac2):
                        subprocess.Popen(["powershell.exe", '&"C:\SAT in Spots we Trust\Error.ps1"'])
                        if(len(myObject.filenames)-1 == fileIdx):
                            nextDonor = 'A'
                            finishedSlideString = logString
                        else:
                            nextDonor = revAminoacids[j+1]
                            finishedSlideString = []
                        ErrorVac1 = tk.Tk()
                        ErrorVac1.geometry("400x85")
                        ErrorVac1.attributes("-topmost", True)
                        ErrorVac1.protocol('WM_DELETE_WINDOW', self.doSomething)
                        ErrorVac1Msg = tk.Label(ErrorVac1, text='A malfunction occured. Please get someone to fix it!')
                        ErrorVac1Msg.pack()
                        EndButton1 = tk.Button(ErrorVac1, text="Exit", command = lambda: self.End(pneumaticsSystem, myObject, i, fid, nextDonor, finishedSlideString = finishedSlideString))
                        EndButton1.pack()
                        continueButton1 = tk.Button(ErrorVac1, text="Continue", command = ErrorVac1.destroy)
                        continueButton1.pack()
                        ErrorVac1.mainloop()
                    
                    robot.MoveJ(safePickUpLocation[j])
                    robot.MoveJ(pickUpLocation[j])
                    pneumaticsSystem.write(b'seta4:0\r')
                    time.sleep(1.0)
                    pneumaticsSystem.write(b'seta5:1\r')
                    time.sleep(2.5)
                    robot.MoveJ(safePickUpLocation[j])
                    pneumaticsSystem.write(b'seta5:0\r')
                    robot.MoveJ(preDropOffLocation[0])
                    
                    # setup information for the following acceptor slide
                    if(fileChange == True):
                        fileChange = False
                    else:
                        fileChange = True
                    
                os.chdir('../..')
                
                # reset error log file 
                fidError = open(r'log_error.txt', 'r')
                listOfStarters = fidError.readlines()
                listOfStarters[i] = 'A' + '\n'
                fidError = open(r'log_error.txt', 'w')
                fidError.writelines(listOfStarters)
                fidError.close()
                
                # acceptor slide transportation and positioning 
                pneumaticsSystem.write(b'seta3:0\r')
                pneumaticsSystem.write(b'seta6:0\r')
                time.sleep(1)
                robot.MoveJ(preDropOffLocation[1])
                robot.MoveJ(dropOffLocation[2])
                pneumaticsSystem.write(b'seta4:1\r')
                time.sleep(3.0)
                robot.MoveJ(preDropOffLocation[1])
                robot.MoveJ(preDropOffLocation[0])
                robot.MoveJ(safePickUpLocation[i])
                robot.MoveJ(pickUpLocation[i])
                pneumaticsSystem.write(b'seta4:0\r')
                time.sleep(1.0)
                pneumaticsSystem.write(b'seta5:1\r')
                time.sleep(5.0)
                robot.MoveJ(safePickUpLocation[i])
                pneumaticsSystem.write(b'seta5:0\r')
                robot.MoveJ(preDropOffLocation[0]) 
                fid.write(logString)
            else:
                logString = myObject.generateJobFiles(ActiveSlideState = i)
                fid.write(logString)
        fid.close()
                
        # move back to the home position and close the pneumatics systme conncetion
        robot.MoveJ(home)
        pneumaticsSystem.close()
###############################################################################

###############################################################################        
    def runDifferentModes(self, myObject, laserObject):
                
        # set up a connection with the pneumatics system
        pneumaticsSystem = serial.Serial('COM6', 57600, timeout=1)
        if(not(pneumaticsSystem.isOpen())):
            pneumaticsSystem.open()
        time.sleep(0.5)
        
        # get an instance of the opend RoboDK software
        RL = robolink.Robolink()
        
        # get the target coordinates
        robot = RL.Item('KUKA KR 3 R540')
        targets = RL.ItemList(ITEM_TYPE_TARGET)
        home = targets[0]
        preDropOffLocation = targets[-6:-4]
        dropOffLocation = targets[-4:-1]
        waitLocation = [targets[-1]]
        notPickUp = len(preDropOffLocation) + len(dropOffLocation) + len(waitLocation)
        pickUpLocation = targets[1:len(targets)-notPickUp:2]
        safePickUpLocation = targets[2:len(targets)-notPickUp:2]
        
        # connect to the robot
        RUN_ON_ROBOT = True
        checkValue = 1        
        robot.setConnectionParams('172.31.1.147', 7000, '/', 'anonymous','')
        while(checkValue):
            try:
                if RUN_ON_ROBOT:
                    # Connect to the robot using default connetion parameters
                    robot.Connect()
                    status, status_msg = robot.ConnectedState()
                    if status != ROBOTCOM_READY:
                        # Stop if the connection did not succeed
                        print(status_msg)
                        raise Exception("Failed to connect: " + status_msg)  
                    # Set to run the robot commands on the robot
                    RL.setRunMode(RUNMODE_RUN_ROBOT)
                    # Note: This is set automatically if we use
                    # robot.Connect() through the API
                checkValue = 0
            except:
                time.sleep(1)
                pass
        
        # move to the home target -> savety        
        robot.MoveJ(home)
        
        # prepare the upload folder for the sld files
        try:
            if(os.path.isfile('C:\Transfer\Transfer.sld')):
                os.remove('C:\Transfer\Transfer.sld')
        except:
            pass
        try:        
            if(os.path.isfile('C:\Transfer\Transfer1.sld')):
                os.remove('C:\Transfer\Transfer1.sld')
        except:
            pass                   
        if(os.path.isfile('C:\Transfer\Transfer.sld')):
            fileChange = False
        else:
            fileChange = True
        
        # check if there are to many images and end the program
        if(len(myObject.fileNames) > 23):
            ErrorImages = tk.Tk()
            ErrorImages.geometry("300x100")
            ErrorImages.attributes("-topmost", True)
            ErrorImages.protocol('WM_DELETE_WINDOW', self.doSomething)
            ErrorImagesMsg = tk.Label(ErrorImages, text='There are to many files to process!')
            ErrorImagesMsg.pack()
            ExitImagesButton = tk.Button(ErrorImages, text="Exit", command = lambda: self.EndDifferentModes(pneumaticsSystem, myObject))
            ExitImagesButton.place(x = 125, y = 50)
            ErrorImages.mainloop()
        
        # transportation procedure
        slidePositions = [1]
        for i in slidePositions:

            # acceptor slide transportation and positioning
            robot.MoveJ(safePickUpLocation[i])
            robot.MoveJ(pickUpLocation[i])
            pneumaticsSystem.write(b'seta4:1\r')
            time.sleep(3.0)
            robot.MoveJ(safePickUpLocation[i])
            robot.MoveJ(preDropOffLocation[0])
            robot.MoveJ(preDropOffLocation[1])
            pneumaticsSystem.write(b'seta6:1\r')
            time.sleep(1)
            robot.MoveJ(dropOffLocation[0])
            pneumaticsSystem.write(b'seta4:0\r')
            time.sleep(1.0)
            pneumaticsSystem.write(b'seta5:1\r')
            time.sleep(5)
            robot.MoveJ(preDropOffLocation[1])
            pneumaticsSystem.write(b'seta5:0\r')
            robot.MoveJ(preDropOffLocation[0])
            pneumaticsSystem.write(b'seta1:1\r')
            pneumaticsSystem.write(b'seta0:1\r')
            time.sleep(5)
            pneumaticsSystem.write(b'seta1:0\r')
            pneumaticsSystem.write(b'seta0:0\r')
            pneumaticsSystem.write(b'seta2:1\r')
            time.sleep(5)
            pneumaticsSystem.write(b'seta2:0\r')
            pneumaticsSystem.write(b'seta1:1\r')
            pneumaticsSystem.write(b'seta0:1\r')
            time.sleep(5)
            pneumaticsSystem.write(b'seta2:1\r')
            time.sleep(5)
            pneumaticsSystem.write(b'seta1:0\r')
            pneumaticsSystem.write(b'seta0:0\r')
            pneumaticsSystem.write(b'seta2:0\r')
            pneumaticsSystem.write(b'seta3:1\r')
            
            # donor slide transportation and positioning
            donorSlidePositions = np.arange(4, 4+len(myObject.fileNames))
            for j in donorSlidePositions:
                
                robot.MoveJ(safePickUpLocation[j])
                robot.MoveJ(pickUpLocation[j])
                pneumaticsSystem.write(b'seta4:1\r')
                time.sleep(3.0)
                robot.MoveJ(safePickUpLocation[j])
                
                # check vacuum sensors for malfunction
                vac1, vac2 = self.vacuumMonitoring(pneumaticsSystem)
                if not(vac1 and vac2):
                    subprocess.Popen(["powershell.exe", '&"C:\SAT in Spots we Trust\Error.ps1"'])
                    ErrorVac1 = tk.Tk()
                    ErrorVac1.geometry("400x85")
                    ErrorVac1.attributes("-topmost", True)
                    ErrorVac1.protocol('WM_DELETE_WINDOW', self.doSomething)
                    ErrorVac1Msg = tk.Label(ErrorVac1, text='A malfunction occured. Please get someone to fix it!')
                    ErrorVac1Msg.pack()
                    EndButton1 = tk.Button(ErrorVac1, text="Exit", command = lambda: self.EndDifferentModes(pneumaticsSystem, myObject))
                    EndButton1.pack()
                    continueButton1 = tk.Button(ErrorVac1, text="Continue", command = ErrorVac1.destroy)
                    continueButton1.pack()
                    ErrorVac1.mainloop()
                
                robot.MoveJ(preDropOffLocation[0])
                robot.MoveJ(preDropOffLocation[1])
                time.sleep(1)
                robot.MoveJ(dropOffLocation[1])
                pneumaticsSystem.write(b'seta4:0\r')
                time.sleep(1.0)
                pneumaticsSystem.write(b'seta5:1\r')
                time.sleep(2.5)
                robot.MoveJ(preDropOffLocation[1])
                pneumaticsSystem.write(b'seta5:0\r')
                robot.MoveJ(preDropOffLocation[0])
                
                # upload the transfer file to laserDESK and wait for a response
                laserObject.uploadJobFile(myObject.fileNames[j-4], fileChange)
                statusLaser = ''
                time.sleep(1.5)
                while(not("b'\\x02\\x08\\x00\\x00\\x00\\x04\\x00\\x00\\x00\\x1f\\xa3\\x01\\x00\\t\\x03'" == statusLaser)):
                    time.sleep(1)
                    statusLaser = laserObject.status()
                if(fileChange):
                    if(os.path.isfile('C:\Transfer\Transfer1.sld')):
                        os.remove('C:\Transfer\Transfer1.sld')
                else:
                    if(os.path.isfile('C:\Transfer\Transfer.sld')):
                        os.remove('C:\Transfer\Transfer.sld')
                        
                # transfer the file 
                laserObject.laserOn()
                statusLaser = ''
                time.sleep(1.5)
                while(not("b'\\x02\\x08\\x00\\x00\\x00\\x04\\x00\\x00\\x00\\x1f\\xa3\\x01\\x00\\t\\x03'" == statusLaser)):
                    time.sleep(1)
                    statusLaser = laserObject.status()
                                               
                robot.MoveJ(preDropOffLocation[1])
                time.sleep(1)
                robot.MoveJ(dropOffLocation[1])
                pneumaticsSystem.write(b'seta4:1\r')
                time.sleep(7.0) 
                robot.MoveJ(preDropOffLocation[1])
                robot.MoveJ(preDropOffLocation[0])
                
                # check vacuum sensors for malfunction
                vac1, vac2 = self.vacuumMonitoring(pneumaticsSystem)
                if not(vac1 and vac2):
                    subprocess.Popen(["powershell.exe", '&"C:\SAT in Spots we Trust\Error.ps1"'])
                    ErrorVac1 = tk.Tk()
                    ErrorVac1.geometry("400x85")
                    ErrorVac1.attributes("-topmost", True)
                    ErrorVac1.protocol('WM_DELETE_WINDOW', self.doSomething)
                    ErrorVac1Msg = tk.Label(ErrorVac1, text='A malfunction occured. Please get someone to fix it!')
                    ErrorVac1Msg.pack()
                    EndButton1 = tk.Button(ErrorVac1, text="Exit", command = lambda: self.EndDifferentModes(pneumaticsSystem, myObject))
                    EndButton1.pack()
                    continueButton1 = tk.Button(ErrorVac1, text="Continue", command = ErrorVac1.destroy)
                    continueButton1.pack()
                    ErrorVac1.mainloop()
                
                robot.MoveJ(safePickUpLocation[j])
                robot.MoveJ(pickUpLocation[j])
                pneumaticsSystem.write(b'seta4:0\r')
                time.sleep(1.0)
                pneumaticsSystem.write(b'seta5:1\r')
                time.sleep(2.5)
                robot.MoveJ(safePickUpLocation[j])
                pneumaticsSystem.write(b'seta5:0\r')
                robot.MoveJ(preDropOffLocation[0])
                
                # setup information for the following acceptor slide
                if(fileChange == True):
                    fileChange = False
                else:
                    fileChange = True
                
            os.chdir('../..')
            
            # acceptor slide transportation and positioning 
            pneumaticsSystem.write(b'seta3:0\r')
            pneumaticsSystem.write(b'seta6:0\r')
            time.sleep(1)
            robot.MoveJ(preDropOffLocation[1])
            robot.MoveJ(dropOffLocation[2])
            pneumaticsSystem.write(b'seta4:1\r')
            time.sleep(3.0)
            robot.MoveJ(preDropOffLocation[1])
            robot.MoveJ(preDropOffLocation[0])
            robot.MoveJ(safePickUpLocation[i])
            robot.MoveJ(pickUpLocation[i])
            pneumaticsSystem.write(b'seta4:0\r')
            time.sleep(1.0)
            pneumaticsSystem.write(b'seta5:1\r')
            time.sleep(5.0)
            robot.MoveJ(safePickUpLocation[i])
            pneumaticsSystem.write(b'seta5:0\r')
            robot.MoveJ(preDropOffLocation[0]) 
                
        # move back to the home position and close the pneumatics systme conncetion
        robot.MoveJ(home)
        pneumaticsSystem.close()
###############################################################################      