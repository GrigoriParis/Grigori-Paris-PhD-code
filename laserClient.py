# -*- coding: utf-8 -*-
"""
Created on Tue Nov 27 09:23:43 2018

@author: gparis
"""
###############################################################################
# imports
import socket
from shutil import copyfile
###############################################################################

###############################################################################
# 
# interaction with the laserDESK server software
#
###############################################################################
class laserDeskClient():

###############################################################################    
    def __init__(self):
        
        # set up some core values
        # buffer size for strings 
        # server ip address 172.31.1.1
        # server entrance port 3000
        # 2 lists to receive server information
        self.BUFFERSIZE = 1024
        self.serverIpAddress = '172.31.1.1'
        self.serverIpPort = 3000
        self.tmpList = []
        self.tmpList2 = []
###############################################################################

###############################################################################
    def telegramWriter(self, commandNumber, parameterList):
        
        # sum of all digits calculation for the checksum
        def sumDigits(n):
            s = 0
            while n:
                s += n % 10
                n //= 10
            return s
        
        # list flattening
        flatten = lambda l: [item for sublist in l for item in sublist]

        # special command numbers
        STX = 2
        ETX = 3
        DLE = 16
        
        # 4 byte long command number
        command = [commandNumber, 0, 0, 0]
        
        # encoded parameterlist for the telegram
        parameterCode = []
        for parameter in parameterList:
            if(type(parameter[0]) == int):
                # ints are encoded in 4 byte
                parameterCode.append([parameter[0], 0, 0, 0])
            elif(type(parameter[0]) == str):
                # strings are encoded letterbased with an additional 0 termination
                # syntax based final 0 termination 
                tmpList = []
                for letter in parameter[0]:
                    tmpList.append([int(letter.encode("utf-8").hex(), 16), 0])
                tmpList.append([0, 0])
                parameterCode.append(flatten(tmpList))
            else:
                # possibly append double and so forth 
                pass
        
        # building the telegrambase
        # dataBlock -> 4 byte long command number and the encoded parameters
        dataBlock = command + flatten(parameterCode)
        # telegramBase -> 4 byte long dataBlock length and the dataBlock
        telegramBase = [len(dataBlock), 0, 0, 0] + dataBlock
        
        # checksum calculation -> last digit of the sum of the telegrambase
        sumOftelegramBase = sumDigits(sum(telegramBase))
        checkSum = int(str(sumOftelegramBase)[-1])
        if(checkSum == STX or checkSum == ETX or checkSum == DLE):
            checkSum = [DLE, checkSum]
        else:
            checkSum = [checkSum]
    
        # readjust the telegram -> fix special command numbers
        telegram = []
        for number in telegramBase:
            if(number == STX or number == ETX or number == DLE):
                telegram.extend([DLE, number])
            else:
                telegram.append(number)
                
        # return telegram
        return bytes([STX]) + bytes(telegram) + bytes(checkSum) + bytes([ETX])
###############################################################################
        
###############################################################################        
    def establishConnection(self):
        
        # open socket and connect to laserDESK
        self.mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.mySocket.connect((self.serverIpAddress, self.serverIpPort))
###############################################################################
        
###############################################################################        
    def closeConnection(self):
        
        # close socket
        self.mySocket.close()
###############################################################################
        
###############################################################################        
    def logIn(self):
        
        # send log in telegram, receive the data, and save it 
        telegram = self.telegramWriter(1, [[r'1990']])
        self.mySocket.sendall(telegram)
        data = self.mySocket.recv(self.BUFFERSIZE)
        self.tmpList.append(data)
###############################################################################
        
###############################################################################        
    def logOff(self):
        
        # send log off telegram, receive the data, and save it 
        telegram = self.telegramWriter(2, [])
        self.mySocket.sendall(telegram)
        data = self.mySocket.recv(self.BUFFERSIZE)
        self.tmpList.append(data)
###############################################################################
        
###############################################################################        
    def remoteOn(self):
        
        # send remote start telegram, receive the data, and save it 
        telegram = self.telegramWriter(5, [])
        self.mySocket.sendall(telegram)
        data = self.mySocket.recv(self.BUFFERSIZE)
        self.tmpList.append(data)
###############################################################################
        
###############################################################################        
    def remoteOff(self):
        
        # send remote end telegram, receive the data, and save it 
        telegram = self.telegramWriter(6, [])
        self.mySocket.sendall(telegram)
        data = self.mySocket.recv(self.BUFFERSIZE)
        self.tmpList.append(data)
###############################################################################
        
###############################################################################        
    def laserOn(self):
        
        # send laser process start telegram, receive the data, and save it 
        telegram = self.telegramWriter(12, [])
        self.mySocket.sendall(telegram)
        data = self.mySocket.recv(self.BUFFERSIZE)
        self.tmpList.append(data)
###############################################################################
        
###############################################################################        
    def status(self):
        
        # send status query telegram, receive the data, save it, and return the latest query
        telegram = self.telegramWriter(4, [])
        self.mySocket.sendall(telegram)
        data = self.mySocket.recv(self.BUFFERSIZE)
        self.tmpList2.append(data)
        return str(data)
###############################################################################
        
###############################################################################        
    def uploadJobFile(self, file, boolean, PCname = r'BSMC-21MRNR2'):
        
        # binary message to local laserDesk server, containing file path, here: 
        # "\\BSMC-21MRNR2\Transfer\Transfer.sld" (= 'C:\Transfer\Transfer.sld')
        if(boolean):
            copyfile(file, 'C:\Transfer\Transfer.sld')
            telegram = self.telegramWriter(7, [[r'\\' + PCname + r'\Transfer\Transfer.sld'], [0]])
            self.mySocket.sendall(telegram)
        else:
            copyfile(file, 'C:\Transfer\Transfer1.sld')
            telegram = self.telegramWriter(7, [[r'\\' + PCname + r'\Transfer\Transfer1.sld'], [0]])
            self.mySocket.sendall(telegram)
        data = self.mySocket.recv(self.BUFFERSIZE)
        self.tmpList.append(data)
###############################################################################