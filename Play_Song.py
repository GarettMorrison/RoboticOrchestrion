from tracemalloc import start
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

# midiName = 'Lavender_Town'
midiName = 'SuperMarioBros_Theme'
# midiName = 'MidiTest'

# alto_trackIndex = 0
# tenor_trackIndex = 1

netTrackIndex = 0


alto_trackIndex = netTrackIndex*2
tenor_trackIndex = netTrackIndex*2 +1

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


    oc.setSolenoid('Tenor_Left', 5200)
    oc.setSolenoid('Tenor_Right', 6000)

    oc.setSolenoid('Alto_Left', 5000)
    oc.setSolenoid('Alto_Right', 7000)

    oc.setStepperDelay('Alto', trackList[alto_trackIndex]['step_delay'])
    oc.setStepperDelay('Tenor', trackList[tenor_trackIndex]['step_delay'])


    for netTrackIndex in range(8):
        alto_trackIndex = netTrackIndex*2
        tenor_trackIndex = netTrackIndex*2 +1

        print(f"Playing tracks {alto_trackIndex} & {tenor_trackIndex}")
        
        altoTrack = trackList[alto_trackIndex]['commands']
        tenorTrack = trackList[tenor_trackIndex]['commands']

        altoIndex = len(altoTrack) -1
        tenorIndex = len(tenorTrack) -1
        time.sleep(2)
        startTime = time.time() + 30

        # while(True):
        #     oc.trigger('Tenor_Right')
        #     time.sleep(1.0)
        #     oc.trigger('Alto_Right')
        #     time.sleep(1.0)
        #     oc.trigger('Tenor_Left')
        #     time.sleep(1.0)
        #     oc.trigger('Alto_Left')
        #     time.sleep(1.0)

        oc.trigger('Tenor_Right')
        time.sleep(1)
        oc.trigger('Tenor_Left')
        time.sleep(0.25)
        oc.trigger('Alto_Right')
        time.sleep(0.25)
        oc.trigger('Alto_Left')
        time.sleep(1)
        
        
        
        while True:
            currTime = time.time() - startTime

            if altoIndex >= 0 and altoTrack[altoIndex][0] < currTime:
                if altoTrack[altoIndex][2] == 'n': # Move command
                    oc.moveStepper('Alto', altoTrack[altoIndex][1])
                    print(f"{round(currTime,1)}   Alto {altoTrack[altoIndex][1]}")
                elif altoTrack[altoIndex][2] == 'L': # Play command
                    oc.trigger('Alto_Left')
                    print(f"{round(currTime,1)}   Alto_Left")
                elif altoTrack[altoIndex][2] == 'R': # Play command
                    oc.trigger('Alto_Right')
                    print(f"{round(currTime,1)}   Alto_Right")
                altoIndex -= 1
                
            if tenorIndex >= 0 and tenorTrack[tenorIndex][0] < currTime:
                if tenorTrack[tenorIndex][2] == 'n': # Move command
                    oc.moveStepper('Tenor', tenorTrack[tenorIndex][1])
                    print(f"{round(currTime,1)}   Tenor {tenorTrack[tenorIndex][1]}")
                elif tenorTrack[tenorIndex][2] == 'L': # Play command
                    oc.trigger('Tenor_Left')
                    print(f"{round(currTime,1)}   Tenor_Left")
                elif tenorTrack[tenorIndex][2] == 'R': # Play command
                    oc.trigger('Tenor_Right')
                    print(f"{round(currTime,1)}   Tenor_Right")
                tenorIndex -= 1
            
            time.sleep(0.001)

            if altoIndex == -1 and tenorIndex == -1:
                print(f"Track finished!")
                break
        
        time.sleep(20)