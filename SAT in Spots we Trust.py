# -*- coding: utf-8 -*-
"""
Created on Tue Sep 17 15:14:50 2019

@author: gparis
"""
###############################################################################
# imports
import subprocess
import time 
import tkinter as tk
import App
import laserClient
###############################################################################


###############################################################################
# function call to negate GUI buttons
def doSomething():
    pass
###############################################################################
    
###############################################################################
# function to set the program choice
global programValue
def setProgram(value, layer):
    global programValue
    programValue = value
    layer.destroy()
###############################################################################

############################################################################### 
# prepare files for email notification
def setValue(YesNo, window):
    global address
    
    # get user-defined email address
    def getAddress(Entry, Layer):
        global address
        address = Entry.get()
        Layer.destroy()
    
    # clear previous window
    window.destroy()
    
    if(YesNo):
        # ask for a user-defined email address
        # obtain the address through getAddress
        addressLayer = tk.Tk()
        addressLayer.protocol('WM_DELETE_WINDOW', doSomething)
        addressLabel = tk.Label(addressLayer, text = "E-mail address")
        addressLabel.pack()
        addressEntry = tk.Entry(addressLayer, bd = 10, width = 50)
        addressEntry.pack()
        OkButton = tk.Button(addressLayer, text = "Confirm", command = lambda: getAddress(addressEntry, addressLayer))
        OkButton.pack()
        addressLayer.mainloop()        
    else:
        address = ''
    
    # define the error and process completion message
    # write the messages into the Done and Error files
    msg1 = r'Send-MailMessage -From BSMC-21MRNR2@mpikg.mpg.de -Subject "Synthesizer cLIFT2 in K-0.170" -SmtpServer "mail.mpikg.mpg.de" -To "%s" -Body "Your process is completed. Please get your acceptor slides."' % address
    msg2 = r'Send-MailMessage -From BSMC-21MRNR2@mpikg.mpg.de -Subject "Synthesizer cLIFT2 in K-0.170" -SmtpServer "mail.mpikg.mpg.de" -To "%s" -Body "An error occured. Please come and look at the problem. Ask if you do not know what to do!"' % address
    outFilename1 = 'Done.ps1'
    outFilename2 = 'Error.ps1'
    with open(outFilename1, 'w') as outFile:    
        parsedLine = msg1
        outFile.write(parsedLine)
    with open(outFilename2, 'w') as outFile:    
        parsedLine = msg2
        outFile.write(parsedLine)
###############################################################################

###############################################################################
# user input for email notification -> setValue call
Email = tk.Tk()
Email.geometry("400x100")
Email.attributes("-topmost", True)
Email.protocol('WM_DELETE_WINDOW', doSomething)
msg = tk.Label(Email, text="Do you want to receive an E-mail notifications?")
msg.pack()
yesButton = tk.Button(Email, text = "Yes", width = 5, command = lambda: setValue(1, Email)) 
yesButton.place(x = 100, y = 50)
noButton = tk.Button(Email, text = "No", width = 5, command = lambda: setValue(0, Email)) 
noButton.place(x = 250, y = 50)
Email.mainloop()
###############################################################################

###############################################################################
# start laserDESK and wait for it to load
# start RoboDK
startLaserDESK = r'C:\SAT in Spots we Trust\LaserDESK.cmd'
subprocess.call(startLaserDESK)
startRoboDK = tk.Tk()
startRoboDK.geometry("300x100")
startRoboDK.attributes("-topmost", True)
startRoboDK.protocol('WM_DELETE_WINDOW', doSomething)
msg = tk.Label(startRoboDK, text="Did LaserDESK load?")
msg.pack()
startRoboDKButton = tk.Button(startRoboDK, text = "Yes", width = 5, command = startRoboDK.destroy) 
startRoboDKButton.place(x = 125, y = 50)
startRoboDK.mainloop()
time.sleep(0.1)
###############################################################################

###############################################################################
# catch RoboDK licence bug -> positions are communicated wrong
# import the robot class and check if something went wrong 
try:
    import robot
    startRobodk = robot.robotControl()
    startRobodk.buildAutomation()
except:
    Error = tk.Tk()
    Error.attributes("-topmost", True)
    Error.geometry("500x100")
    Error_msg = tk.Label(Error, text="Error! Restart, if you don't want to break something!")
    Error_msg.pack()
    Error.mainloop()

import robot
###############################################################################

###############################################################################
# generate laserCLient object
# establish connection to laserDESK
# log into laserDESK
# start the remote
startLaserDesk = laserClient.laserDeskClient()
startLaserDesk.establishConnection()
startLaserDesk.logIn()
startLaserDesk.remoteOn()
###############################################################################

###############################################################################
# ask which program should be run
programChoice = tk.Tk()
programChoice.attributes("-topmost", True)
programChoice.protocol('WM_DELETE_WINDOW', doSomething)
programChoice.geometry("1150x150")
programChoiceSynthesisButton = tk.Button(programChoice, text = "Synthesis", command = lambda: setProgram(1, programChoice))
programChoiceSynthesisButton.place(x = 100, y = 60, height = 30, width = 150)
programChoiceStaticFilesButton = tk.Button(programChoice, text = "Generate Synthesis files", command = lambda: setProgram(2, programChoice))
programChoiceStaticFilesButton.place(x = 300, y = 60, height = 30, width = 150)
programChoicePhotoIrradiationButton = tk.Button(programChoice, text = "Photo irradiation", command = lambda: setProgram(3, programChoice))
programChoicePhotoIrradiationButton.place(x = 500, y = 60, height = 30, width = 150)
programChoiceRunStaticFilesButton = tk.Button(programChoice, text = "Process laserDESK files", command = lambda: setProgram(4, programChoice))
programChoiceRunStaticFilesButton.place(x = 700, y = 60, height = 30, width = 150)
programChoiceStackingFilesButton = tk.Button(programChoice, text = "Stacking mode", command = lambda: setProgram(5, programChoice))
programChoiceStackingFilesButton.place(x = 900, y = 60, height = 30, width = 150)
programChoice.mainloop()
###############################################################################

###############################################################################
# start GUI and build the folder structure
root = tk.Tk()
root.attributes("-topmost", True)
root.protocol('WM_DELETE_WINDOW', doSomething)
myApp = App.Application(root, programValue)
root.mainloop()
###############################################################################

###############################################################################
# start the transportations procedure
myMove = robot.robotControl()
if(programValue == 1):
    myMove.run(myApp, startLaserDesk)
elif(programValue == 3):
    myMove.runDifferentModes(myApp, startLaserDesk)
elif(programValue == 4):
    myMove.runDifferentModes(myApp, startLaserDesk)
elif(programValue == 5):
    myMove.runDifferentModes(myApp, startLaserDesk)
###############################################################################

###############################################################################
# send the completion notification and end the process
subprocess.Popen(["powershell.exe", '&"C:\SAT in Spots we Trust\Done.ps1"'])
Finish = tk.Tk()
Finish.geometry("200x100")
Finish.attributes("-topmost", True)
FinishButton = tk.Button(Finish, text="Done", command = Finish.destroy)
FinishButton.place(x = 75, y = 25, width = 50, height = 50)
Finish.mainloop()
subprocess.Popen(["powershell.exe", '&"C:\SAT in Spots we Trust\FinalKill.ps1"'])
###############################################################################