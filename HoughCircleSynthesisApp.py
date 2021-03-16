# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 14:33:21 2020

@author: gparis
"""

import HoughCircleSynthesis
import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory

def disable_event():
    pass

def Done():
    global outputFileName
    outputFileName = Entry.get()
    root.destroy()

root = tk.Tk()
root.withdraw() # now somehow bugged, start once without and then it works
filePath = askopenfilename(title = 'Choose the image for processing')
displayImageFilePath = askopenfilename(title = 'Choose the image for displaying')
evalFilePath = askopenfilename(title = 'Choose the image for evaluation')
outputFileDir = askdirectory(title = 'Choose the results directory')
root.title()
root.geometry("428x34")
root.iconbitmap()
root.protocol("WM_DELETE_WINDOW", disable_event)
root.resizable(False, False)
labelText = tk.StringVar()
labelText.set('Enter a name for the results file')
tk.Label(root, textvariable = labelText, height = 1).grid(row = 1, column = 1)
Entry = tk.Entry(root)
Entry.grid(row = 1, column = 2)
tk.Button(root, text = 'Done', command = Done).grid(row = 1, column = 3)
root.deiconify()

root.mainloop()

controlSynthesis = HoughCircleSynthesis.HoughCircleSynthesis(filePath, displayImageFilePath, evalFilePath, outputFileDir, outputFileName)

