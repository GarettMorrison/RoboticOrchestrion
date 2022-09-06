#!/usr/bin/python

import pyFuncs.AudioFuncs as af
import pyFuncs.OrchestrionControl as oc
import pyFuncs.AudioManager as am
from pyFuncs.NoteData import *

from matplotlib import pyplot as plt
import time
import math as m
import statistics as st
import numpy as np
from copy import deepcopy
import pickle as pkl
import yaml

# Temp variables (Hopefully generalize eventually)
testString = 'Alto'
testSolenoid = 'Alto_Right'
testString = 'Tenor'
testSolenoid = 'Tenor_Right'

testRes = 100

if __name__ == '__main__':
    mechanismName = 'DualStrikeString'

    yaml_path = 'MusicData/Mechanism/' + mechanismName + '.yaml'
    print(f"Loading {yaml_path}") 
    mech_yaml = yaml.load( open(yaml_path), Loader=yaml.FullLoader)

    for tag in mech_yaml:
        # print(tag)
        print(f"   {tag} : {mech_yaml[tag]}")
    print("")

    position_min = mech_yaml['position_min']    
    position_max = mech_yaml['position_max']
    step_delay = mech_yaml['step_delay']
    solenoid_dur = mech_yaml['solenoid_dur']

    am.amSetup()
    oc.OC_init()
    # Open serial ports
    time.sleep(1) # Delay 1 second to allow Arduino to start up


    oc.setSolenoid(testSolenoid, solenoid_dur)
    oc.setStepperDelay(testString, step_delay)


    def checkPoint():
        oc.setSolenoid(testSolenoid, solenoid_dur +2000)
        am.measureAndSavePoint(testSolenoid)
        
        oc.setSolenoid(testSolenoid, solenoid_dur +1000)
        am.measureAndSavePoint(testSolenoid)
        
        oc.setSolenoid(testSolenoid, solenoid_dur)
        am.measureAndSavePoint(testSolenoid)
        
        oc.setSolenoid(testSolenoid, solenoid_dur -1000)
        am.measureAndSavePoint(testSolenoid)
        
        oc.setSolenoid(testSolenoid, solenoid_dur -2000)
        am.measureAndSavePoint(testSolenoid)

    # while True:
    #     checkPoint()
    #     time.sleep(1)


    print(f"Moving Forward")
    testPos = testRes * m.ceil(position_min/testRes)

    while testPos < position_max:
        print(f"Testing pos {testPos}")
        oc.moveToPos(testString, testPos)
        checkPoint()
        testPos += testRes
        
    testPos -= testRes

    print(f"Moving Backward")
    while testPos > position_min:
        print(f"Testing pos {testPos}")
        oc.moveToPos(testString, testPos)
        checkPoint()
        testPos -= testRes
        
    print(f"Moving to zero")
    oc.moveToPos(testString, 0)
