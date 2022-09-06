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
import yaml
import pyFuncs.MidiProccessing as pymidi

import pyFuncs.AudioFuncs as af
import pyFuncs.AudioManager as am

duplicateCount = 9
noteDur = 1.0
preHitDur = 0.25

noteDur = 0.0
preHitDur = 0.0

voiceSet = {}

def loadInstrument(instrumentName):
    global voiceSet

    yaml_path = 'MusicData/Instruments/' + instrumentName + '/settings.yaml'
    print(f"Loading {yaml_path}") 
    instrumentData = yaml.load( open(yaml_path), Loader=yaml.FullLoader)

    pitchPkl_path = open("MusicData/Instruments/" + instrumentName + "/noteRange.pkl", 'rb')
    print(f"Loading {pitchPkl_path}")
    instrumentData['notes'] = pkl.load(pitchPkl_path)
    instrumentData['notes']['pos'] = instrumentData['notes']['pos'].astype(int)

    voiceSet[instrumentName] = instrumentData
    return(instrumentData)

loadInstrument('Alto')
loadInstrument('Tenor')



# Plot note range of instruments
plotIter = 0
labelSet = []
for voiceName in voiceSet:
    fooVoice = voiceSet[voiceName]

    # print(f"\n\n{voiceName}")
    # for foo in fooVoice['notes']: print(f"   {foo}")

    labelSet.append(voiceName)
    plt.scatter(
        [plotIter for ii in range(len(fooVoice['notes']['number']))],
        fooVoice['notes']['number'],
        color='blue',
        )

    plotIter += 1



# midiName = "FreeBird_Solo"
midiName = "WiiMenu_Short"
# midiName = "WetHands"
# midiName = "Curses_AlexYoder"
# midiName = "Curses_AlexYoder_RORC"
# midiName = "Lavender_Town"
# midiName = "MidiTest"
# midiName = "Sweden"
midiName = "SuperMarioBros_Theme"

midiData = pymidi.loadMidiData("MiDi/" + midiName + ".mid")

print(f"\n\nVoices")
for voiceName in voiceSet:
    fooVoice = voiceSet[voiceName]
    print(f"   {voiceName}:     {min(fooVoice['notes']['number'])}->{max(fooVoice['notes']['number'])}")

print(f"\nTracks")
for fooTrack in midiData:
    try:
        foo_note = np.array(fooTrack['note'])
        print(f"   {fooTrack['title']}:     {min(foo_note)}->{max(foo_note)}")
    except:
        continue

    labelSet.append(fooTrack['title'])
    plt.scatter(
        [plotIter for ii in range(len(foo_note))],
        foo_note,
        color='orange',
        )

    plotIter += 1

print(f"\n\n")

plt.xticks(range(plotIter), labelSet)
plt.show()