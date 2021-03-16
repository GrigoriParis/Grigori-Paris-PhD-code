# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 13:45:00 2020

@author: gparis
"""

import cv2
import numpy as np
import sys
import tkinter as tk
from tkinter.filedialog import askopenfilename
from matplotlib import colors
import pandas as pd
import os

class HoughCircleSynthesis():
    
    def __init__(self, imageFilePath, displayImageFilePath, evaluatioImagePath, outputFileDir, outputFileName, par1 = 30, par2 = 11, acc = 1, minDist = 50, minRad = 2,
                 maxRad = 100, font = cv2.FONT_HERSHEY_SIMPLEX, fontScale = 0.5, height = 40, maxResize = 8, pixelSize = 1.87646,#1.87646,5, 2.309616
                 blur = 9, resize = 2, textColor = 'blue', circleColor = 'yellow', 
                 textColorAdd = 'yellow', circleColorAdd = 'blue', VSI = True):
        
        self.VSI = VSI
        self.par1 = par1
        self.par2 = par2
        self.acc = acc
        self.minDist = minDist
        self.minRad = minRad
        self.maxRad = maxRad
        self.resize = resize       
        self.font = font
        self.fontScale = 0.5
        self.height = height
        self.maxResize = maxResize
        self.pixelSize = pixelSize
        self.NoneType = type(None)
        self.imgOriginal = cv2.imread(displayImageFilePath, cv2.IMREAD_UNCHANGED)
        self.ImgEval = cv2.imread(evaluatioImagePath, cv2.IMREAD_UNCHANGED)
        self.outputFileDir = outputFileDir
        self.outputFileName = outputFileName
        self.deleteSpots = []
        self.img = cv2.imread(imageFilePath, cv2.IMREAD_GRAYSCALE)
        self.img = cv2.medianBlur(self.img, blur)
        self.bgrColorCodeCircle = colors.to_rgb(circleColor)[::-1]
        self.bgrColorCodeText = colors.to_rgb(textColor)[::-1]
        self.bgrColorCodeCircleAdd = colors.to_rgb(circleColorAdd)[::-1]
        self.bgrColorCodeTextAdd = colors.to_rgb(textColorAdd)[::-1]
        self.bgrColorCodeCircle = (int(self.bgrColorCodeCircle[0]*255), int(self.bgrColorCodeCircle[1]*255), int(self.bgrColorCodeCircle[2]*255))
        self.bgrColorCodeText = (int(self.bgrColorCodeText[0]*255), int(self.bgrColorCodeText[1]*255), int(self.bgrColorCodeText[2]*255))
        self.bgrColorCodeCircleAdd = (int(self.bgrColorCodeCircleAdd[0]*255), int(self.bgrColorCodeCircleAdd[1]*255), int(self.bgrColorCodeCircleAdd[2]*255))
        self.bgrColorCodeTextAdd = (int(self.bgrColorCodeTextAdd[0]*255), int(self.bgrColorCodeTextAdd[1]*255), int(self.bgrColorCodeTextAdd[2]*255))
        
        if(len(self.ImgEval.shape) > 2):
            print('You did not submit a grayscale image for evaluation. Please reconsider.')
            sys.exit()
        
        self.showTransformation()
        self.addSpots()
        self.addMissingSpots()
        
        if(self.VSI):
            self.analyzeVSI()
        else:
            self.analyze()
    
    def nothing(self, x):
        pass
    
    def disable_event(self):
        pass
    
    def showTransformation(self):        

        windowName = 'Stage 1: Detected circles by HoughTransformation - Press q to continue'
        cv2.namedWindow(windowName, cv2.WINDOW_AUTOSIZE)
#        cv2.namedWindow(windowName, cv2.WND_PROP_FULLSCREEN)
#        cv2.setWindowProperty(windowName, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        cv2.createTrackbar('param1', windowName, self.par1, 300, self.nothing) # 62
        cv2.createTrackbar('param2', windowName, self.par2, 100, self.nothing) # 15
#        cv2.createTrackbar('accumulator size', windowName, self.acc, 4, self.nothing) # 1
        cv2.createTrackbar('min distance', windowName, self.minDist, 50, self.nothing) # 20
        cv2.createTrackbar('min radius', windowName, self.minRad, 100, self.nothing) # 2
        cv2.createTrackbar('max radius', windowName, self.maxRad, 100, self.nothing) # 15
        cv2.createTrackbar('resize', windowName, self.resize, self.maxResize, self.nothing)
        tmp = cv2.getWindowImageRect(windowName)
        ySizeImg, xSizeImg, _ = self.imgOriginal.shape 
        threshold = 50
        if(ySizeImg*self.maxResize > tmp[3]):
            cv2.createTrackbar('y', windowName, 0, ySizeImg*self.maxResize-tmp[3]+threshold, self.nothing)
        else:
            cv2.createTrackbar('y', windowName, 0, 0, self.nothing)
            
        if(xSizeImg*self.maxResize > tmp[2]):
            cv2.createTrackbar('x', windowName, 0, xSizeImg*self.maxResize-tmp[2]+threshold, self.nothing)
        else:
            cv2.createTrackbar('x', windowName, 0, 0, self.nothing)

        visit = 0
        checkChange = False
        while(True):
    
            self.numberList = []
            cimg = self.imgOriginal.copy() 
            try:
                
                par1Tmp = self.par1
                par2Tmp = self.par2
                accTmp = self.acc
                minDistTmp = self.minDist
                maxRadTmp = self.maxRad
                minRadTmp = self.minRad
                resizeTmp = self.resize
                if not checkChange:
                    
                    self.circles = cv2.HoughCircles(self.img, cv2.HOUGH_GRADIENT, self.acc, self.minDist,
                                            param1 = self.par1, param2 = self.par2, minRadius = self.minRad, maxRadius = self.maxRad)
                    
                    tmpOrder = self.circles[0][:,1].copy()
                    tmpOrderCopy = self.circles[0][:,1].copy()
                    self.minDist = 20
                    startValue = 0
                    while(tmpOrder.size != 0):
                        minValue = min(tmpOrder)
                        tmpOrder = np.ma.MaskedArray(tmpOrder, np.logical_and(tmpOrder < minValue + self.minDist/4, tmpOrder > startValue)).compressed()
                        tmpOrderCopy[np.logical_and(tmpOrderCopy < minValue + self.minDist/4, tmpOrderCopy > startValue)] = minValue
                        startValue = minValue
            #    self.circles = np.uint16(np.around(self.circles))               
                if type(self.circles) == self.NoneType:
                    
                    print('Something is wrong!')
                    pass
                else:
                    
                    self.orderedCircles = self.circles[0][np.lexsort((np.sqrt(self.circles[0][:,0]**2+self.circles[0][:,1]**2), tmpOrderCopy))]
                    for number, (x, y, r) in enumerate(self.orderedCircles, start=1):
                        
                        text = str(number)
                        (tw, th), bl = cv2.getTextSize(text, self.font, self.fontScale, 2)      # So the text can be centred in the circle
                        tw /= 2
                        th = th / 2 + 2
                        cv2.circle(cimg, (x, y), r, self.bgrColorCodeCircle, 1)
#                        cv2.rectangle(cimg, (int(x - tw), int(y - th)), (int(x + tw), int(y + th)), (255, 0, 0), -1)
                        cv2.putText(cimg, text, (int(x-tw), int(y + bl)), self.font, self.fontScale, self.bgrColorCodeText, 1, cv2.LINE_4)
                        self.numberList.append(number)
                
                self.par1 = cv2.getTrackbarPos('param1', windowName)
                self.par2 = cv2.getTrackbarPos('param2', windowName)
#                self.acc = cv2.getTrackbarPos('accumulator size', windowName)
                self.minDist = cv2.getTrackbarPos('min distance', windowName)
                self.maxRad = cv2.getTrackbarPos('max radius', windowName)
                self.minRad = cv2.getTrackbarPos('min radius', windowName)
                self.resize = cv2.getTrackbarPos('resize', windowName)
                y = cv2.getTrackbarPos('y', windowName)
                x = cv2.getTrackbarPos('x', windowName)
                if(self.par1 == 0):
                    self.par1 = 1
                if(self.par2 == 0):
                    self.par2 = 1
                if(self.acc == 0):
                    self.acc = 1  
                if(self.minDist == 0):
                    self.minDist = 1
                if(self.resize == 0):
                    self.resize = 1
                
                checkChange = par1Tmp == self.par1 and par2Tmp == self.par2 and accTmp == self.acc and \
                              minDistTmp == self.minDist and maxRadTmp == self.maxRad and minRadTmp == self.minRad and \
                              resizeTmp == self.resize                                 
                width = int(cimg.shape[1] * self.resize)
                height = int(cimg.shape[0] * self.resize)               
                dsize = (width, height)
                
                k = cv2.waitKey(1) & 0xFF == ord('q')
                if k:
                    tmpCimg = cimg
                    break
                
                cimg = cv2.resize(cimg, dsize)
                if(cimg.shape[1] <= tmp[2]):
                    x = 0
                elif(cimg.shape[1] - x <= tmp[2]):
                    x = int(cimg.shape[1] - tmp[2])
                if(cimg.shape[0] <= tmp[3]):
                    y = 0
                elif(cimg.shape[0] - y <= tmp[3]):
                    y = int(cimg.shape[0] - tmp[3])
                cv2.imshow(windowName, cimg[y:, x:])
#                cv2.imshow(windowName, cimg)
#                cv2.namedWindow(windowName, cv2.WND_PROP_FULLSCREEN)
#                cv2.setWindowProperty(windowName, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

                # some displaying bug forced me to do this
                if not visit:
                    
                    visit = visit + 1
                    cv2.setTrackbarPos('resize', windowName, 2)
                elif visit == 1:
                    
                    visit = visit + 1
                    cv2.setTrackbarPos('resize', windowName, 1)
                
            except:
                print('Think before you do something!')
                sys.exit()
            
        cv2.destroyAllWindows()
        
        def saveValues():
            self.deleteSpots = [i for i in range(len(Vars)) if not Vars[i].get()]
            cv2.destroyAllWindows()
            root.destroy()
        
        def Close():            
            cv2.destroyAllWindows()
            root.destroy()
            sys.exit()
            
        def showSpots(tmpCimg):
            windowName = 'Stage 2: Remove non-wanted spots from list - press q to close'
            cv2.namedWindow(windowName, cv2.WINDOW_AUTOSIZE)
            
            if(ySizeImg*self.maxResize > tmp[3]):
                cv2.createTrackbar('y', windowName, 0, ySizeImg*self.maxResize-tmp[3]+threshold, self.nothing)
            else:
                cv2.createTrackbar('y', windowName, 0, 0, self.nothing)
                
            if(xSizeImg*self.maxResize > tmp[2]):
                cv2.createTrackbar('x', windowName, 0, xSizeImg*self.maxResize-tmp[2]+threshold, self.nothing)
            else:
                cv2.createTrackbar('x', windowName, 0, 0, self.nothing)
                
            cv2.createTrackbar('resize', windowName, self.resize, self.maxResize, self.nothing)
            
            while(True):
                
                cimgCopy = tmpCimg.copy()
                
                y = cv2.getTrackbarPos('y', windowName)
                x = cv2.getTrackbarPos('x', windowName)
                self.resize = cv2.getTrackbarPos('resize', windowName)
                
                if(self.resize == 0):
                    self.resize = 1
                    
                width = int(cimgCopy.shape[1] * self.resize)
                height = int(cimgCopy.shape[0] * self.resize)               
                dsize = (width, height)
                cimgCopy = cv2.resize(cimgCopy, dsize)
                if(cimgCopy.shape[1] <= tmp[2]):
                    x = 0
                elif(cimgCopy.shape[1] - x <= tmp[2]):
                    x = int(cimgCopy.shape[1] - tmp[2])
                if(cimgCopy.shape[0] <= tmp[3]):
                    y = 0
                elif(cimgCopy.shape[0] - y <= tmp[3]):
                    y = int(cimgCopy.shape[0] - tmp[3])
                cv2.imshow(windowName, cimgCopy[y:, x:])
                
                k = cv2.waitKey(1) & 0xFF == ord('q')
                if k:
                    break
                
            cv2.destroyAllWindows()                
        
        root = tk.Tk()
        root.title('Stage 2')
        root.iconbitmap()
        root.geometry('400x300')
        root.protocol("WM_DELETE_WINDOW", self.disable_event)
        root.resizable(False, False)
        
        text = tk.Text(root, cursor = 'arrow')
        vsb = tk.Scrollbar(root, command = text.yview)
        button = tk.Button(root, wraplength = 80, text = 'Save and continue', command = saveValues)
        button2 = tk.Button(root, text = 'Close', command = Close)
        button3 = tk.Button(root, text = 'Show spots', command = lambda: showSpots(tmpCimg))
        text.configure(yscrollcommand = vsb.set)
        
        button.pack()
        button.place(bordermode = tk.OUTSIDE, height = 75, width = 100, x = 250, y = 18.75)
        button2.pack()
        button2.place(bordermode = tk.OUTSIDE, height = 75, width = 100, x = 250, y = 112.5)
        button3.pack()
        button3.place(bordermode = tk.OUTSIDE, height = 75, width = 100, x = 250, y =  206.25)
        vsb.pack()
        vsb.place(width = 20, relheight = 1, x = 180)
        text.pack()
        text.place(width = 200, height = 300)
        
        checkbuttons = []
        Vars = []
        
        for i in self.numberList:
            
            var = tk.IntVar(value = 1)
            cb = tk.Checkbutton(text, text="Spot #%s" % i,
                                variable = var, onvalue = 1, offvalue = 0)
            text.window_create("end", window = cb)
            text.insert("end", "\n")
            checkbuttons.append(cb)
            Vars.append(var)
        text.configure(state="disabled")
        
        root.mainloop()
        
    def addSpots(self):
        
        def addValues():
            if type(self.circlesTmp) == self.NoneType:
                pass
            elif(self.circlesTmp.size == 0):
                pass
            else:
                idxList = []
                for i in range(len(Listbox2.get(0, tk.END))):
                    
                    idx = int(Listbox2.get(i)[6:]) - 1
                    idxList.append(idx)
                    self.orderedCirclesCopy = np.insert(self.orderedCirclesCopy, self.deleteSpots[i], self.circlesTmp[idx], axis=0)
                    self.numberListCopy = np.insert(self.numberListCopy, self.deleteSpots[i], np.asarray(self.numberList)[self.deleteSpots[i]])
                self.deleteSpots = np.delete(self.deleteSpots, np.arange(len(Listbox2.get(0, tk.END))))
                self.circlesTmp = np.delete(self.circlesTmp, idxList, axis=0)
                Listbox2.delete(0, tk.END)
        
        def setValue(event):
            if(Listbox1.get(tk.ANCHOR) == ''):
                Listbox1.delete(tk.ANCHOR)
            else:
                Listbox2.insert(tk.END, Listbox1.get(tk.ANCHOR))
                Listbox1.delete(tk.ANCHOR)
        
        def setValueBack(event):
            if(Listbox2.get(tk.ANCHOR) == ''):
                Listbox2.delete(tk.ANCHOR)
            else:
                Listbox1.insert(tk.END, Listbox2.get(tk.ANCHOR))
                Listbox2.delete(tk.ANCHOR)
        
        def Continue(frame):
            frame.destroy()
            cv2.destroyAllWindows()
            self.leave = 1
                    
        
        def drawCircle(event, x, y, flags, param):
            global ix, iy
            if event == cv2.EVENT_LBUTTONDOWN:
                
                ix, iy = x, y
                self.drawing = True
            elif event == cv2.EVENT_MOUSEMOVE:
                
                if self.drawing == True:
                    r = np.sqrt(((x - ix)/self.resize)**2 + ((y - iy)/self.resize)**2)
                    self.fullCircleTmp = np.array([(self.xCor+x)/self.resize, (self.yCor+y)/self.resize, r], dtype=np.float32).reshape(1, 3)
            elif event == cv2.EVENT_LBUTTONUP: 
                
                r = np.sqrt(((x - ix)/self.resize)**2 + ((y - iy)/self.resize)**2)
                tmp = np.array([(self.xCor+x)/self.resize, (self.yCor+y)/self.resize, r], dtype=np.float32).reshape(1, 3)
                if type(self.circlesTmp) == self.NoneType:
                    self.circlesTmp = tmp
                else:
                    self.circlesTmp = np.append(self.circlesTmp, tmp, axis=0)
                self.drawing = False
                self.fullCircleTmp = None
                
        
        windowName = 'Stage 3: Add new spots (1 - flush, 2 - flush last, 3 - add in order, 4 - add with order, q - continue)'
        cv2.namedWindow(windowName)
        
        cv2.setMouseCallback(windowName, drawCircle)
#        cv2.setMouseCallback(windowName, lambda event,x,y,flags,param: drawCircle(event,x,y,flags,param, cimg))
        cv2.createTrackbar('resize', windowName, self.resize, self.maxResize, self.nothing)
        
        tmp = cv2.getWindowImageRect(windowName)
        ySizeImg, xSizeImg, _ = self.imgOriginal.shape 
        threshold = 50
        
        if(ySizeImg*self.maxResize > tmp[3]):
            cv2.createTrackbar('y', windowName, 0, ySizeImg*self.maxResize-tmp[3]+threshold, self.nothing)
        else:
            cv2.createTrackbar('y', windowName, 0, 0, self.nothing)
            
        if(xSizeImg*self.maxResize > tmp[2]):
            cv2.createTrackbar('x', windowName, 0, xSizeImg*self.maxResize-tmp[2]+threshold, self.nothing)
        else:
            cv2.createTrackbar('x', windowName, 0, 0, self.nothing)
            
        cv2.createTrackbar('resize', windowName, self.resize, self.maxResize, self.nothing)
        
        self.orderedCirclesCopy = np.delete(self.orderedCircles, self.deleteSpots, axis=0)
        self.numberListCopy = np.delete(np.asarray(self.numberList), self.deleteSpots)
        
        self.drawing = False
        self.circlesTmp = None
        self.fullCircleTmp = None
        self.leave = 0
        
        while(True):
            
            cimg = self.imgOriginal.copy()
            
            for number, (x, y, r) in zip(self.numberListCopy, self.orderedCirclesCopy):
                text = str(number)
                (tw, th), bl = cv2.getTextSize(text, self.font, self.fontScale, 2)      # So the text can be centred in the circle
                tw /= 2
                th = th / 2 + 2
                cv2.circle(cimg, (x, y), r, self.bgrColorCodeCircle, 1)
#                cv2.rectangle(cimg, (int(x - tw), int(y - th)), (int(x + tw), int(y + th)), (0, 128, 255), -1)
                cv2.putText(cimg, text, (int(x-tw), int(y + bl)), self.font, self.fontScale, self.bgrColorCodeText, 1, cv2.LINE_4)
            
            if not type(self.circlesTmp) == self.NoneType:
                for number, (x, y, r) in zip(np.arange(1, len(self.circlesTmp)+1), self.circlesTmp):
                    text = str(number)
                    (tw, th), bl = cv2.getTextSize(text, self.font, self.fontScale, 2)      # So the text can be centred in the circle
                    tw /= 2
                    th = th / 2 + 2
                    cv2.circle(cimg, (x, y), r, self.bgrColorCodeCircleAdd, 1)
    #                cv2.rectangle(cimg, (int(x - tw), int(y - th)), (int(x + tw), int(y + th)), (0, 128, 255), -1)
                    cv2.putText(cimg, text, (int(x-tw), int(y + bl)), self.font, self.fontScale, self.bgrColorCodeTextAdd, 1, cv2.LINE_4)
                    
            if not type(self.fullCircleTmp) == self.NoneType:
                cv2.circle(cimg, (self.fullCircleTmp[0][0], self.fullCircleTmp[0][1]), self.fullCircleTmp[0][2], self.bgrColorCodeCircleAdd, -1)           
            
            self.resize = cv2.getTrackbarPos('resize', windowName)
            if(self.resize == 0):
                self.resize = 1
            
            self.yCor = cv2.getTrackbarPos('y', windowName)
            self.xCor = cv2.getTrackbarPos('x', windowName)            
            width = int(cimg.shape[1] * self.resize)
            height = int(cimg.shape[0] * self.resize)           
            dsize = (width, height)
            cimg = cv2.resize(cimg, dsize)
            
            if(cimg.shape[1] <= tmp[2]):
                self.xCor = 0
            elif(cimg.shape[1] - self.xCor <= tmp[2]):
                self.xCor = int(cimg.shape[1] - tmp[2])
            if(cimg.shape[0] <= tmp[3]):
                self.yCor = 0
            elif(cimg.shape[0] - self.yCor <= tmp[3]):
                self.yCor = int(cimg.shape[0] - tmp[3])
            cv2.imshow(windowName, cimg[self.yCor:, self.xCor:])
            
            result = cv2.waitKey(1) & 0xFF   
            if result == ord('q'):
                cv2.destroyAllWindows()
                break
            elif result == ord('4'):

                if type(self.circlesTmp) == self.NoneType:
                    print('Draw spots first')
                    continue
                elif len(self.circlesTmp) > len(self.deleteSpots):
                    print('You have drawn to many spots')
                    continue
                else:
                    root = tk.Tk()
                    root.title('Stage 3')
                    root.iconbitmap()
                    root.geometry("400x300")
                    root.protocol("WM_DELETE_WINDOW", self.disable_event)
                    root.resizable(False, False)
                    
                    vsb1 = tk.Scrollbar(root, orient=tk.VERTICAL)
                    vsb2 = tk.Scrollbar(root, orient=tk.VERTICAL)
                    Listbox1 = tk.Listbox(root, yscrollcomman=vsb1.set)
                    Listbox2 = tk.Listbox(root, yscrollcomman=vsb2.set)
                    button1 = tk.Button(root, text = 'Save', command = addValues)
                    button2 = tk.Button(root, text = 'Return', command = root.destroy)
                    button3 = tk.Button(root, text = 'Continue', command = lambda: Continue(root))
                    
                    button1.pack()
                    button1.place(bordermode = tk.OUTSIDE, height = 75, width = 100, x = 25, y = 212.5)
                    button2.pack()
                    button2.place(bordermode = tk.OUTSIDE, height = 75, width = 100, x = 150, y = 212.5)
                    button3.pack()
                    button3.place(bordermode = tk.OUTSIDE, height = 75, width = 100, x = 275, y = 212.5)
                    Listbox1.pack()
                    Listbox1.place(width = 180, height = 200, x = 0)
                    Listbox2.pack()
                    Listbox2.place(width = 180, height = 200, x = 200)
                    vsb1.pack()
                    vsb1.place(width = 20, height = 200, x = 180)
                    vsb2.pack()
                    vsb2.place(width = 20, height = 200, x = 380)
                    
                    for i in range(len(self.circlesTmp)):
                        Listbox1.insert(tk.END, 'Spot # ' + str(i+1))
                                        
                    Listbox1.bind('<Double-Button-1>', setValue)
                    Listbox2.bind('<Double-Button-1>', setValueBack)
                                        
                    root.mainloop()
                    
                    if self.leave:
                        break
                    
            elif result == ord('3'):
                if type(self.circlesTmp) == self.NoneType:
                    print('Draw spots first')
                    continue
                elif len(self.circlesTmp) > len(self.deleteSpots):
                    print('You have drawn to many spots')
                    continue
                else:
                    for i in range(len(self.circlesTmp)):
                        self.orderedCirclesCopy = np.insert(self.orderedCirclesCopy, self.deleteSpots[i], self.circlesTmp[i], axis=0)
                        self.numberListCopy = np.insert(self.numberListCopy, self.deleteSpots[i], np.asarray(self.numberList)[self.deleteSpots[i]])
                    self.deleteSpots = np.delete(self.deleteSpots, np.arange(len(self.circlesTmp)))
                    self.circlesTmp = None
                    continue
            elif result == ord('2'):
                self.circlesTmp = self.circlesTmp[:-1]
                continue
            elif result == ord('1'):
                self.circlesTmp = None
                continue
        
    def addMissingSpots(self):
        
        def addValues():
            if type(self.circlesTmp) == self.NoneType:
                pass
            elif(self.circlesTmp.size == 0):
                pass
            else:
                outOfBounds = False
                idxList = []
                numberList = []
                for i in range(len(EntryList)-1, -1, -1):
                    if not EntryList[i].get() == '':
                        try:
                            int(EntryList[i].get())
                            isInt = True
                        except ValueError:
                            isInt = False
                        if isInt:
                            if len(self.orderedCirclesCopy) >= int(EntryList[i].get()):
                                numberList.append(int(LabelTextList[i].get()[6:])-1)
                                idxList.append(int(EntryList[i].get())-1)
                                EntryList[i].destroy()
                                del EntryList[i]
                                LabelList[i].destroy()
                                del LabelList[i]
                                del LabelTextList[i]
                            else:
                                outOfBounds = True
                        else:
                            print(str(EntryList[i].get()) + ' is not a valid entry! Please try again.')
                            EntryList[i].delete(0, tk.END)
                    else:
                        pass 
                    
                self.orderedCirclesCopy = np.insert(self.orderedCirclesCopy, np.asarray(idxList), self.circlesTmp[numberList], axis=0)
                self.circlesTmp = np.delete(self.circlesTmp, numberList, axis=0)
                
                if outOfBounds:
                    print(str(EntryList[i].get()) + ' is not within the found spot range. Please label them in order and submit.')
                
                root.destroy()
        
        def Continue(frame):
            self.orderedCirclesCopy = np.append(self.orderedCirclesCopy, self.circlesTmp, axis=0)
            self.circlesTmp = None
            frame.destroy()
            cv2.destroyAllWindows()
            self.leave = 1
                    
        
        def drawCircle(event, x, y, flags, param):
            global ix, iy
            if event == cv2.EVENT_LBUTTONDOWN:
                
                ix, iy = x, y
                self.drawing = True
            elif event == cv2.EVENT_MOUSEMOVE:
                
                if self.drawing == True:
                    r = np.sqrt(((x - ix)/self.resize)**2 + ((y - iy)/self.resize)**2)
                    self.fullCircleTmp = np.array([(self.xCor+x)/self.resize, (self.yCor+y)/self.resize, r], dtype=np.float32).reshape(1, 3)
            elif event == cv2.EVENT_LBUTTONUP: 
                
                r = np.sqrt(((x - ix)/self.resize)**2 + ((y - iy)/self.resize)**2)
                tmp = np.array([(self.xCor+x)/self.resize, (self.yCor+y)/self.resize, r], dtype=np.float32).reshape(1, 3)
                if type(self.circlesTmp) == self.NoneType:
                    self.circlesTmp = tmp
                else:
                    self.circlesTmp = np.append(self.circlesTmp, tmp, axis=0)
                self.drawing = False
                self.fullCircleTmp = None
                
        
        windowName = 'Stage 4: Add missing spots (1 - flush, 2 - flush last, 3 - add in order, 4 - add with position, 5 - add to the beginning,  q - continue)'
        cv2.namedWindow(windowName)
        
        cv2.setMouseCallback(windowName, drawCircle)
        cv2.createTrackbar('resize', windowName, self.resize, self.maxResize, self.nothing)
        
        tmp = cv2.getWindowImageRect(windowName)
        ySizeImg, xSizeImg, _ = self.imgOriginal.shape 
        threshold = 50
        
        if(ySizeImg*self.maxResize > tmp[3]):
            cv2.createTrackbar('y', windowName, 0, ySizeImg*self.maxResize-tmp[3]+threshold, self.nothing)
        else:
            cv2.createTrackbar('y', windowName, 0, 0, self.nothing)
            
        if(xSizeImg*self.maxResize > tmp[2]):
            cv2.createTrackbar('x', windowName, 0, xSizeImg*self.maxResize-tmp[2]+threshold, self.nothing)
        else:
            cv2.createTrackbar('x', windowName, 0, 0, self.nothing)
        
        self.drawing = False
        self.circlesTmp = None
        self.fullCircleTmp = None
        self.leave = 0
        
        while(True):
            
            cimg = self.imgOriginal.copy()
            
            for number, (x, y, r) in enumerate(self.orderedCirclesCopy, start = 1):
                text = str(number)
                (tw, th), bl = cv2.getTextSize(text, self.font, self.fontScale, 2)      # So the text can be centred in the circle
                tw /= 2
                th = th / 2 + 2
                cv2.circle(cimg, (x, y), r, self.bgrColorCodeCircle, 1)
#                cv2.rectangle(cimg, (int(x - tw), int(y - th)), (int(x + tw), int(y + th)), (0, 128, 255), -1)
                cv2.putText(cimg, text, (int(x-tw), int(y + bl)), self.font, self.fontScale, self.bgrColorCodeText, 1, cv2.LINE_4)
            
                if not type(self.circlesTmp) == self.NoneType:
                    for number, (x, y, r) in enumerate(self.circlesTmp, start = 1):
                        text = str(number)
                        (tw, th), bl = cv2.getTextSize(text, self.font, self.fontScale, 2)      # So the text can be centred in the circle
                        tw /= 2
                        th = th / 2 + 2
                        cv2.circle(cimg, (x, y), r, self.bgrColorCodeCircleAdd, 1)
        #                cv2.rectangle(cimg, (int(x - tw), int(y - th)), (int(x + tw), int(y + th)), (0, 128, 255), -1)
                        cv2.putText(cimg, text, (int(x-tw), int(y + bl)), self.font, self.fontScale, self.bgrColorCodeTextAdd, 1, cv2.LINE_4)
                        
                if not type(self.fullCircleTmp) == self.NoneType:
                    cv2.circle(cimg, (self.fullCircleTmp[0][0], self.fullCircleTmp[0][1]), self.fullCircleTmp[0][2], self.bgrColorCodeCircleAdd, -1)           
            
            self.resize = cv2.getTrackbarPos('resize', windowName)
            if(self.resize == 0):
                self.resize = 1
                
            self.yCor = cv2.getTrackbarPos('y', windowName)
            self.xCor = cv2.getTrackbarPos('x', windowName)
            width = int(cimg.shape[1] * self.resize)
            height = int(cimg.shape[0] * self.resize)           
            dsize = (width, height)
            cimg = cv2.resize(cimg, dsize)
            
            if(cimg.shape[1] <= tmp[2]):
                self.xCor = 0
            elif(cimg.shape[1] - self.xCor <= tmp[2]):
                self.xCor = int(cimg.shape[1] - tmp[2])
            if(cimg.shape[0] <= tmp[3]):
                self.yCor = 0
            elif(cimg.shape[0] - self.yCor <= tmp[3]):
                self.yCor = int(cimg.shape[0] - tmp[3])
            cv2.imshow(windowName, cimg[self.yCor:, self.xCor:])
            
            result = cv2.waitKey(1) & 0xFF   
            if result == ord('q'):
                
                cv2.destroyAllWindows()
                break
            elif result == ord('5'):
                self.orderedCirclesCopy = np.insert(self.orderedCirclesCopy, 0, self.circlesTmp, axis=0)
                self.circlesTmp = None
                continue
            elif result == ord('4'):
    
                if type(self.circlesTmp) == self.NoneType:
                    print('Draw spots first')
                    continue
                else:
                    root = tk.Tk()
                    root.title('Stage 4')
                    root.iconbitmap()
                    root.geometry("400x300")
                    root.protocol("WM_DELETE_WINDOW", self.disable_event)
                    root.resizable(False, False)
                    frame = tk.Frame(root)
                    canvasFrame = tk.Canvas(frame)
                    
                    vsb = tk.Scrollbar(frame, orient = tk.VERTICAL, command=canvasFrame.yview)
                    scrollableFrame = tk.Frame(canvasFrame)
                    
                    scrollableFrame.bind(
                        "<Configure>",
                        lambda e: canvasFrame.configure(
                            scrollregion=canvasFrame.bbox("all")
                        )
                    )
                    
                    canvasFrame.create_window((0, 0), window = scrollableFrame, anchor = "nw")
                    canvasFrame.configure(yscrollcommand=vsb.set)
                    
                    LabelList = []
                    LabelTextList = []
                    EntryList = []
                    large_font = ('Verdana', 10)
                    for i in range(len(self.circlesTmp)):
                        labelText = tk.StringVar()
                        labelText.set('Spot # ' + str(i+1))
                        Label = tk.Label(scrollableFrame, textvariable = labelText, height = 1)
                        Label.grid(row = i, column = 1, sticky = 'W')
                        LabelList.append(Label)
                        LabelTextList.append(labelText)
                        Entry = tk.Entry(scrollableFrame, width = 400, font=large_font)
                        Entry.grid(row = i, column = 2, sticky = 'E')
                        EntryList.append(Entry)
                    button1 = tk.Button(root, wraplength = 80, text = 'Save and return', command = addValues)
                    button2 = tk.Button(root, text = 'Return', command = root.destroy)
                    button3 = tk.Button(root, wraplength = 80, text = 'Add in order and continue', command = lambda: Continue(root))
                    
                    frame.pack()
                    frame.place(width = 400, height = 200, x = 0)
                    canvasFrame.pack(side="left")
                    button1.pack()
                    button1.place(bordermode = tk.OUTSIDE, height = 75, width = 100, x = 25, y = 212.5)
                    button2.pack()
                    button2.place(bordermode = tk.OUTSIDE, height = 75, width = 100, x = 150, y = 212.5)
                    button3.pack()
                    button3.place(bordermode = tk.OUTSIDE, height = 75, width = 100, x = 275, y = 212.5)
                    vsb.pack(side="right", fill="y")
                    vsb.place(width = 20, height = 200, x = 380)
                                        
                    root.mainloop()
                    
                    if self.leave:
                        break
                    
            elif result == ord('3'):
                self.orderedCirclesCopy = np.append(self.orderedCirclesCopy, self.circlesTmp, axis=0)
                self.circlesTmp = None
                continue
            elif result == ord('2'):
                self.circlesTmp = self.circlesTmp[:-1]
                continue
            elif result == ord('1'):
                self.circlesTmp = None
                continue
            
    def analyze(self):
        
        self.evalList = []
        self.evalSurface = []
        
        tmpXminus = self.orderedCirclesCopy[:, 0].astype(dtype=np.int32) - self.orderedCirclesCopy[:, 2].astype(dtype=np.int32)
        tmpXplus = self.orderedCirclesCopy[:, 0].astype(dtype=np.int32) + self.orderedCirclesCopy[:, 2].astype(dtype=np.int32)
        tmpYminus = self.orderedCirclesCopy[:, 1].astype(dtype=np.int32) - self.orderedCirclesCopy[:, 2].astype(dtype=np.int32)
        tmpYplus = self.orderedCirclesCopy[:, 1].astype(dtype=np.int32) + self.orderedCirclesCopy[:, 2].astype(dtype=np.int32) 
            
        self.imgSliceList = [self.ImgEval[tmpYminus[i]:tmpYplus[i]+1, tmpXminus[i]:tmpXplus[i]+1] for i in range(len(self.orderedCirclesCopy))]
        
        for Slice in self.imgSliceList:

            midPoint = int(len(Slice)/2)
            xx, yy = np.meshgrid(np.arange(len(Slice)), np.arange(len(Slice)))
            
            self.evalList.append((Slice*((xx - midPoint)**2 + (yy - midPoint)**2 <= midPoint**2)) \
                                 [np.nonzero((Slice*((xx - midPoint)**2 + (yy - midPoint)**2 <= midPoint**2)))])
            self.evalSurface.append(np.pi*(midPoint*self.pixelSize)**2)
        
        self.evalMean = [evalValue.mean() for evalValue in self.evalList]
        self.evalMedian = [np.median(evalValue) for evalValue in self.evalList]
        self.evalPeak = [evalValue.max() for evalValue in self.evalList]
            
        valueList = np.array((self.evalMean, self.evalMedian, self.evalPeak, self.evalSurface)).transpose()
            
        df = pd.DataFrame(valueList, columns = ['Mean [a.u.]', 'Median [a.u.]', 'Peak [a.u.]', 'Surface [Image unit^2]'])
        
        root = tk.Tk()
        root.withdraw()
        filename = askopenfilename(title = 'Choose a file containing the sequence names')
        root.destroy()
        
        nameFrame = pd.read_excel(filename)
        df.insert(0, 'Sequence', nameFrame['Sequence'])
        os.chdir(self.outputFileDir)
        df.to_excel(self.outputFileName + '.xlsx', index = False)
            
        
    def analyzeVSI(self):
        
        self.evalList = []
        self.evalSurface = []
        self.evalDiameter = []
        
        tmpXminus = self.orderedCirclesCopy[:, 0].astype(dtype=np.int32) - self.orderedCirclesCopy[:, 2].astype(dtype=np.int32)
        tmpXplus = self.orderedCirclesCopy[:, 0].astype(dtype=np.int32) + self.orderedCirclesCopy[:, 2].astype(dtype=np.int32)
        tmpYminus = self.orderedCirclesCopy[:, 1].astype(dtype=np.int32) - self.orderedCirclesCopy[:, 2].astype(dtype=np.int32)
        tmpYplus = self.orderedCirclesCopy[:, 1].astype(dtype=np.int32) + self.orderedCirclesCopy[:, 2].astype(dtype=np.int32) 
            
        self.imgSliceList = [self.ImgEval[tmpYminus[i]:tmpYplus[i]+1, tmpXminus[i]:tmpXplus[i]+1] for i in range(len(self.orderedCirclesCopy))]
        
        for Slice in self.imgSliceList:
            
            endPoints = [Slice[0,0], Slice[0,-1], Slice[-1,0], Slice[-1,-1]]
            levelThreshold = (max(np.asarray(endPoints, dtype=np.float32)) + min(np.asarray(endPoints, dtype=np.float32)))/2
            Slice = np.clip(Slice-levelThreshold, a_min = 0, a_max = Slice.max())
            
            midPoint = int(len(Slice)/2)
            xx, yy = np.meshgrid(np.arange(len(Slice)), np.arange(len(Slice)))
            
            self.evalList.append((Slice*((xx - midPoint)**2 + (yy - midPoint)**2 <= midPoint**2)) \
                                 [np.nonzero((Slice*((xx - midPoint)**2 + (yy - midPoint)**2 <= midPoint**2)))])
            self.evalSurface.append(np.pi*(midPoint*self.pixelSize)**2)
            self.evalDiameter.append(2*midPoint*self.pixelSize)
        
        self.evalSum = [evalValue.sum() for evalValue in self.evalList]
        self.evalMean = [evalValue.mean() for evalValue in self.evalList]
        self.evalMedian = [np.median(evalValue) for evalValue in self.evalList]
        self.evalPeak = [evalValue.max() for evalValue in self.evalList]
            
        valueList = np.array((self.evalDiameter, self.evalSum, self.evalMean, self.evalMedian, self.evalPeak,)).transpose()
            
        df = pd.DataFrame(valueList, columns = ['Diameter [Image unit]', 'Intensity sum [a.u.]', 'Mean [a.u.]', 'Median [a.u.]', 'Peak [a.u.]'])
        
        root = tk.Tk()
        root.withdraw()
        filename = askopenfilename(title = 'Choose a file containing the sequence names')
        root.destroy()
        
        nameFrame = pd.read_excel(filename)
        df.insert(0, 'Sequence', nameFrame['Sequence'])
        os.chdir(self.outputFileDir)
        df.to_excel(self.outputFileName + '.xlsx', index = False)            
            
            
            
    
            