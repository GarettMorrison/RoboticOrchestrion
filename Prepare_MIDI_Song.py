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

duplicateCount = 8
noteDur = 2.0
preHitDur = 1.0

transposeCount = 0
startTime = -60
endTime = 60

# noteDur = 0.0
# preHitDur = 0.0

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

# for foo in voiceSet:
#     print(f"{foo}:{voiceSet[foo]}")






# midiName = "FreeBird_Solo"
# midiName = "WiiMenu_Short"
# midiName = "WetHands"


midiName = "Curses_AlexYoder_RORC"
transposeCount = -3
startTime = -30
endTime = 20
tempo = 0.005

# midiName = "Lavender_Town"
# tempo = 0.005

# midiName = "MidiTest"
# tempo = 0.005

midiName = "SuperMarioBros_Theme"
transposeCount = -16
startTime = -30
endTime = 25
tempo = 0.004


midiData = pymidi.loadMidiData("MiDi/" + midiName + ".mid")

# # Plot midi data
# fig, ax = plt.subplots(len(midiData))
# colSet = ['orange', 'blue', 'green']
# pltIter = 0
# for fooTrack in midiData:
#     foo_note = np.array(fooTrack['note'])
#     foo_start = np.array(fooTrack['start'])
#     foo_end = np.array(fooTrack['end'])
#     # for ii in range(len(foo_note)): print(f"{foo_note[ii]}   {foo_start[ii]}   {foo_end[ii]-foo_start[ii]}")

#     for ii in range(len(foo_note)): ax[pltIter].plot([foo_start[ii], foo_end[ii]], [foo_note[ii], foo_note[ii]], color = 'orange')
#     pltIter += 1

#     print(f"{fooTrack['title']}: max {max(foo_note)}   min {min(foo_note)}")

# plt.show()
# # print( midiData )

# Get array of just strikes and times
notes = []
ii = 0
for fooDict in midiData:
    print(f"\n\n")
    # if ii > 0: continue
    # ii += 1

    # if 'tempo' in fooDict:
    #     tempo = fooDict['tempo'] / 1000000.0 / 4
    #     print(f"tempo set to {tempo}")

    for ii in range(len(fooDict['start'])):
        fooDict['start'][ii] *= tempo
    notes += zip(np.array(fooDict['note'])+transposeCount, fooDict['start'])

notes.sort(key = lambda x: x[1])

# print('\n\n')
# for foo in notes: print(foo)
# exit()

print('\n\n')
# Print note matches to instruments
noteSet, noteTimes = zip(*notes)

playableNotes = []
for fooVoice in voiceSet:
    fooDict = voiceSet[fooVoice]
    inRange = 0
    fooNotes = []
    for fooNote in noteSet:
        if fooNote >= min(fooDict['notes']['number']) and fooNote <= max(fooDict['notes']['number']):
            inRange += 1

            if fooNote not in fooNotes:
                fooNotes.append(fooNote)
    
    if len(fooNotes) >0: print(f"{fooVoice}: {inRange}/{len(noteSet)} notes playable     ({min(fooNotes)}->{max(fooNotes)})       voice range:({min(fooDict['notes']['number'])}->{max(fooDict['notes']['number'])} or {fooDict['notes']['name'][-1]}->{fooDict['notes']['name'][0]})")
    else: print(f"{fooVoice}: {inRange}/{len(noteSet)} notes playable       voice range:({min(fooDict['notes']['number'])}->{max(fooDict['notes']['number'])} or {fooDict['notes']['name'][-1]}->{fooDict['notes']['name'][0]})")
    playableNotes += fooNotes
    voiceSet[fooVoice]['playable_range'] = len(fooNotes)
    voiceSet[fooVoice]['playable_count'] = inRange

print(f"{len(list(set(playableNotes)))}/{len(list(set(noteSet)))} tones playable     ({min(playableNotes)}->{max(playableNotes)}) out of ({min(noteSet)}->{max(noteSet)})")
print('\n\n\n')

# for fooVoice in voiceSet:
#     fooDict = voiceSet[fooVoice]
#     print(fooVoice)
#     for foo in fooDict:
#         print(f"   {foo}:{fooDict[foo]}")
#     print('\n')

# Make actual output tracks
trackList = []
for ii in range(duplicateCount):
    for fooVoice in voiceSet:
        trackList.append({
            'voice':fooVoice,
            'notes':voiceSet[fooVoice]['notes'],
            'step_delay':voiceSet[fooVoice]['step_delay'],
            'commands':[(notes[-1][1]+endTime, 0, 'n')],
        })





# for fooDict in trackList:
#     for foo in fooDict:
#         print(f"   {foo}:{fooDict[foo]}")
#     print('\n')


def calcSteppperMove(pos1, pos2, delay):
    # print(f" pos1:{pos1}    pos2:{pos2}    delay:{delay}      movetime:{abs((pos1 - pos2) * delay / 1000000.0)}")
    return(abs((pos1 - pos2) * delay / 1000000.0))


# Iterate over all notes and assign to tracks
while len(notes) > 0:
    fooNote = notes[-1]
    del notes[-1]
    
    # Queue note to track that is already playing it if true
    noteWasPlayed = False
    for ii in range(len(trackList)):
        fooDict = trackList[ii]
        if not fooNote[0] in fooDict['notes']['number']: continue # Continue if never able to play note
        
        notePos = fooDict['notes']['pos'][np.where(fooDict['notes']['number'] == fooNote[0])[0][0]]
        noteTime = fooNote[1]

        nextComm = fooDict['commands'][-1]
        nextTime = nextComm[0]
        nextPos = nextComm[1]

        if notePos == nextPos: # Found string which could play note without moving
            fooDict['commands'].append( (noteTime, notePos, nextComm[2]) ) # command to strike current note
            print(f"Note to track {ii}:{fooNote}    {fooNote[0]} t={round(fooNote[1],1)}     {fooDict['commands'][-2]} & {fooDict['commands'][-1]}        moveTime:{moveTime}, solenoid:{strikeSolenoid}")
            noteWasPlayed = True
            break
    if noteWasPlayed: continue
        



    noteFound = False
    for ii in range(len(trackList)):
        fooDict = trackList[ii]
        if not fooNote[0] in fooDict['notes']['number']: continue # Continue if never able to play note

        notePos = fooDict['notes']['pos'][np.where(fooDict['notes']['number'] == fooNote[0])[0][0]]
        noteTime = fooNote[1]

        nextComm = fooDict['commands'][-1]
        nextTime = nextComm[0]
        nextPos = nextComm[1]

        moveTime = calcSteppperMove(notePos, nextPos, fooDict['step_delay'])
        if moveTime == 0 or len(fooDict['commands']) == 1:
            noteFound = True
            strikeSolenoid = 'L'
        elif moveTime < nextTime - (noteTime + noteDur + preHitDur):
            noteFound = True
            strikeSolenoid = 'L'
        else:
            notePos *= -1
            moveTime = calcSteppperMove(notePos, nextPos, fooDict['step_delay'])

            if moveTime < nextTime - (noteTime + noteDur + preHitDur):
                noteFound = True
                strikeSolenoid = 'R'
        
        if noteFound:
            if nextPos != notePos: fooDict['commands'].append( (nextTime - moveTime - preHitDur, nextPos, 'n') ) # command to move to next position
            fooDict['commands'].append( (noteTime, notePos, strikeSolenoid) ) # command to strike current note

            print(f"Note to track {ii}:{fooNote}    {fooNote[0]} t={round(fooNote[1],1)}     {fooDict['commands'][-2]} & {fooDict['commands'][-1]}        moveTime:{moveTime}, solenoid:{strikeSolenoid}")
            break

    if not noteFound: 
        # input(f"****Unable to play note {fooNote}, continue?")
        print(f"Unable to play note {fooNote}, exiting")
        exit()



print('\n\n')
print(f"Song contains {len(trackList)} tracks")
for ii in range(len(trackList)): 
    if len(trackList[ii]['commands']) > 1: print(f"   track {ii}: {trackList[ii]['voice']} {len(trackList[ii]['commands'])} notes")

# Add initial motions
for ii in range(len(trackList)):
    fooDict = trackList[ii]
    
    nextComm = fooDict['commands'][-1]
    nextTime = nextComm[0]
    nextPos = nextComm[1]

    fooDict['commands'].append( (startTime, nextPos, 'n') ) # Start moving the second the track has begun


outPkl = open("Midi/" + midiName + ".pkl", 'wb')
pkl.dump(trackList, outPkl)
outPkl.close()





# Plot tracks
for fooTrack in trackList[1:]:
    if len(fooTrack['commands']) == 2: continue

    displayOffset = 0
    if fooTrack['voice'] == 'Tenor': displayOffset = -8000
    strike_time = []
    strike_note = []

    move_time = []
    move_pos = []
    prevPos = 0
    for fooComm in reversed(fooTrack['commands']):
        if fooComm[2] == 'n':
            move_time.append(fooComm[0])
            move_pos.append(prevPos + displayOffset)
            
            move_time.append(fooComm[0] + calcSteppperMove(prevPos, fooComm[1], fooDict['step_delay']))
            move_pos.append(fooComm[1] + displayOffset)
            prevPos = fooComm[1]
            
        else:
            strike_time.append(fooComm[0])
            strike_note.append(fooComm[1] + displayOffset)
    
    plt.plot(move_time, move_pos)
    plt.scatter(strike_time, strike_note)
    # break
    
plt.ylabel("Position")
plt.xlabel("Time (s)")
plt.show()