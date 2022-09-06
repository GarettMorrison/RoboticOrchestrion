import pyFuncs.AudioFuncs as af
import pyFuncs.OrchestrionControl as oc
import pyFuncs.AudioManager as am

from matplotlib import pyplot as plt
import time
import math as m
import statistics as st
import numpy as np
from copy import deepcopy
import pickle as pkl

midiName = 'Lavender_Town'

alto_trackIndex = 0
tenor_trackIndex = 1


def calcSteppperMove(pos1, pos2, delay):
    # print(f" pos1:{pos1}    pos2:{pos2}    delay:{delay}      movetime:{abs((pos1 - pos2) * delay / 1000000.0)}")
    return(abs((pos1 - pos2) * delay / 1000000.0))
    
if __name__ == '__main__':
    readFile = open("Midi/" + midiName + ".pkl", 'rb')
    trackList = pkl.load(readFile)
    readFile.close()

    # Print track info
    print(f"Playing song {midiName}")
    print(f"Song contains {len(trackList)} tracks")
    for ii in range(len(trackList)): print(f"   track {ii}: {trackList[ii]['voice']} {len(trackList[ii]['commands'])} notes")
    print('\n')

    am.amSetup()
    oc.OC_init()
    
    # Open serial ports
    time.sleep(1) # Delay 1 second to allow Arduino to start up


    oc.setSolenoid('Tenor_Left', 6000)
    oc.setSolenoid('Tenor_Right', 6000)

    oc.setSolenoid('Alto_Left', 6000)
    oc.setSolenoid('Alto_Right', 6000)

    oc.setStepperDelay('Alto', trackList[alto_trackIndex]['step_delay'])
    oc.setStepperDelay('Tenor', trackList[tenor_trackIndex]['step_delay'])


    for ii in range(len(trackList[tenor_trackIndex]['notes']['number'])):
        if not trackList[tenor_trackIndex]['notes']['number'][ii] in trackList[alto_trackIndex]['notes']['number']: continue

        tenorPos = trackList[tenor_trackIndex]['notes']['pos'][ii]
        altoPos = trackList[alto_trackIndex]['notes']['pos'][np.where(trackList[alto_trackIndex]['notes']['number'] == trackList[tenor_trackIndex]['notes']['number'][ii])[0][0]]

        print(f"Testing {trackList[tenor_trackIndex]['notes']['name'][ii]}     alto:{altoPos}   tenor:{tenorPos}")

        delayTime = max([
            calcSteppperMove(oc.stepperData['Alto']['pos'], altoPos, trackList[alto_trackIndex]['step_delay']),
            calcSteppperMove(oc.stepperData['Tenor']['pos'], tenorPos, trackList[tenor_trackIndex]['step_delay']),
        ])
        
        oc.moveStepper('Tenor', tenorPos)
        oc.moveStepper('Alto', altoPos)

        time.sleep(delayTime)

        for jj in range(4):
            oc.trigger('Tenor_Left')
            oc.trigger('Alto_Left')
            time.sleep(0.5)
        
    oc.moveStepper('Tenor', 0)
    oc.moveStepper('Alto', 0)

    # altoTrack = trackList[alto_trackIndex]['commands']
    # tenorTrack = trackList[tenor_trackIndex]['commands']

    # altoIndex = len(altoTrack) -1
    # tenorIndex = len(tenorTrack) -1
    # time.sleep(1)
    # startTime = time.time() + 30
    
    # oc.trigger('Tenor_Right')
    # time.sleep(0.25)
    # oc.trigger('Alto_Right')
    # time.sleep(0.5)
    # oc.trigger('Tenor_Left')
    # time.sleep(0.25)
    # oc.trigger('Alto_Left')
    # time.sleep(0.75)
    
    # while True:
    #     currTime = time.time() - startTime

    #     if altoIndex >= 0 and altoTrack[altoIndex][0] < currTime:
    #         if altoTrack[altoIndex][2] == 'n': # Move command
    #             oc.moveStepper('Alto', altoTrack[altoIndex][1])
    #             print(f"{round(currTime,1)}   Alto {altoTrack[altoIndex][1]}")
    #         elif altoTrack[altoIndex][2] == 'R': # Move command
    #             oc.trigger('Alto_Right')
    #             print(f"{round(currTime,1)}   Alto_Right")
    #         elif altoTrack[altoIndex][2] == 'L': # Move command
    #             oc.trigger('Alto_Left')
    #             print(f"{round(currTime,1)}   Alto_Left")
    #         altoIndex -= 1
            
    #     if tenorIndex >= 0 and tenorTrack[tenorIndex][0] < currTime:
    #         if tenorTrack[tenorIndex][2] == 'n': # Move command
    #             oc.moveStepper('Tenor', tenorTrack[tenorIndex][1])
    #             print(f"{round(currTime,1)}   Tenor {tenorTrack[tenorIndex][1]}")
    #         elif tenorTrack[tenorIndex][2] == 'R': # Move command
    #             oc.trigger('Tenor_Right')
    #             print(f"{round(currTime,1)}   Tenor_Right")
    #         elif tenorTrack[tenorIndex][2] == 'L': # Move command
    #             oc.trigger('Tenor_Left')
    #             print(f"{round(currTime,1)}   Tenor_Left")
    #         tenorIndex -= 1
        
    #     time.sleep(0.001)

    #     if altoIndex == -1 and tenorIndex == -1:
    #         print(f"Track finished!")
    #         exit()