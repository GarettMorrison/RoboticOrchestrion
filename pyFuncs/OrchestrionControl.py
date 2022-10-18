
from matplotlib import pyplot as plt
import serial
import sys
import time
import struct
import os
import math as m
import statistics as st
import numpy as np
import pickle as pkl
from copy import deepcopy
from multiprocessing import Process, Manager
import pyaudio
import random as r

import serial.tools.list_ports



SERIAL_PORT = 'COM7'
port = None

def OC_init():
    global port
    print('OrchestrionControl: Opening Serial Port')
    try:
        port = serial.Serial(SERIAL_PORT, baudrate=19200, timeout=0)#, rtscts=True)
    except:
        print(f'\nSerial port {SERIAL_PORT} was not able to be opened')
        
        # List comports for easy access
        ports = serial.tools.list_ports.comports()
        print("\nThe following ports are available:")
        for port, desc, hwid in sorted(ports): print("{}: {} [{}]".format(port, desc, hwid))
        exit()



# Solenoid functions and info
solenoidData = {
    'Alto_Right': {'duration': 5000, 'index':2},
    'Tenor_Right': {'duration': 5000, 'index':1},
    'Alto_Left': {'duration': 6000, 'index':3},
    'Tenor_Left': {'duration': 5000, 'index':4},
}

def trigger(solSel):
    global solenoidData
    port.write(int(solenoidData[solSel]['index']).to_bytes(1, 'little', signed=False)) # Send byte indicating to trigger
    
def setSolenoid(solSel, delayMicroseconds):
    global solenoidData
    # Instruction byte solenoid index +4 indicates settting solenoid time  
    port.write(int(solenoidData[solSel]['index'] +4).to_bytes(1, 'little', signed=False))
    
    # Actually send delay
    port.write(int(delayMicroseconds).to_bytes(4, 'little', signed=False))
    solenoidData[solSel]['duration'] = delayMicroseconds



# Stepper functions and info
stepperData = {
    'Alto': {'pos': 0, 'prevPos': 0, 'stepDelay': 4000, 'index': 10},
    'Tenor': {'pos': 0, 'prevPos': 0, 'stepDelay': 4000, 'index': 9},
}

def moveStepper(stepSel, targetPos): # Set stepper target position
    global stepperData
    port.write(int(stepperData[stepSel]['index']).to_bytes(1, 'little', signed=False))  # Instruction byte
    port.write(int(targetPos).to_bytes(4, 'little', signed=True))   # Write target pos
    stepperData[stepSel]['prevPos'] = stepperData[stepSel]['pos']   # Update previous position
    stepperData[stepSel]['pos'] = targetPos # Update current position

def calcStepperTime(stepSel, stepDiff): # Calculate time it will take stepper to reach position
    global stepperData
    return(abs(stepDiff * stepperData[stepSel]['stepDelay'] / 1000000.0))

def moveToPos(stepSel, targetPos): # Move stpper to position, wait until move is complete
    global stepperData
    moveStepper(stepSel, targetPos)
    sleepTime = calcStepperTime(stepSel, stepperData[stepSel]['pos'] - stepperData[stepSel]['prevPos'])
    # print(f'sleepTime:{sleepTime}')
    time.sleep(sleepTime)

def zeroStepper(stepSel): # Set stepper position to 0
    global stepperData
    # Instruction byte stepper index +2 indicates setting stepper position to 0
    port.write(int(stepperData[stepSel]['index'] +2).to_bytes(1, 'little', signed=False))  # Instruction byte


def setStepperDelay(stepSel, delayMicroseconds):
    global stepperData
    # Instruction byte stepper index +4 indicates settting stepper time  
    port.write(int(stepperData[stepSel]['index'] +4).to_bytes(1, 'little', signed=False))
    # Actually send delay
    port.write(int(delayMicroseconds).to_bytes(4, 'little', signed=False))
    stepperData[stepSel]['stepDelay'] = delayMicroseconds

