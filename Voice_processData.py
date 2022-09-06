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

import pyFuncs.AudioFuncs as af



instrumentName = 'Alto'
# instrumentName = 'Tenor'

peakIndex = 0 # First set of motions
# peakIndex = 1 # Second set of motions

readFilePath = 'MusicData/Instruments/'+instrumentName+'/noteRec.pkl'







print("Loading Peaks!")

pitchData_fileName = "MusicData/Instruments/" + instrumentName + "/noteRec.pkl"
pklFile = open(pitchData_fileName, 'rb')
pklDict = pkl.load(pklFile)
pklFile.close()

RATE = pklDict['FS_RATE']

# print(f"pklDict:{pklDict}")

print(f"pklDict:")
for foo in pklDict: print(f"   {foo}")
# plt.scatter(pklDict['stepper_position'], pklDict['calc_pitch'], alpha = 0.3)
# plt.show()

def loadPeaks(fooDict):
    outData = []
    ii = 0

    frqs = []
    pos = []
    signi = []
    while fooDict['stepper_position'][ii] <= fooDict['stepper_position'][ii+1]:
        # if ii > 100: break
        fooSig = fooDict['signal'][ii]
        fooPos = fooDict['stepper_position'][ii]

        print(f"{len(pos)}\033[1A")
        freqs, amps = af.getHarmonic(RATE, fooSig)
        foo_frqs, foo_amps = af.FFT_Peaks(freqs, amps)
        frqs += list(foo_frqs)
        signi += [foo/max(foo_amps) for foo in foo_amps]

        # print(fooDict['solenoid_played'])
        if 'Right' in fooDict['solenoid_played']: pos += [-1*fooPos for foo in foo_frqs]
        else: pos += [fooPos for foo in foo_frqs]
        
        ii += 1
    outData.append( [pos, frqs, signi] )
    print(f"frqs:{len(frqs)}")
    print(f"pos:{len(pos)}")
    print(f"signi:{len(signi)}")

    return(outData)

    frqs = []
    pos = []
    signi = []
    while ii < len(fooDict['stepper_position']):
        fooSig = fooDict['signal'][ii]
        fooPos = fooDict['stepper_position'][ii]

        print(f"{len(pos)}\033[1A")
        freqs, amps = af.getHarmonic(RATE, fooSig)
        foo_frqs, foo_amps = af.FFT_Peaks(freqs, amps)
        frqs += foo_frqs
        signi += [foo/max(foo_amps) for foo in foo_amps]
        pos += [fooPos for foo in foo_frqs]
        ii += 1
    outData.append( [pos, frqs, signi] )
    print(f"frqs:{len(frqs)}")
    print(f"pos:{len(pos)}")
    print(f"signi:{len(signi)}")

    return(outData)

peakData = loadPeaks(pklDict)
pos = np.array(peakData[peakIndex][0])
frq = np.array(peakData[peakIndex][1])
sig = np.array(peakData[peakIndex][2])/max(peakData[peakIndex][2])










print("\n\n\nFITTING DATA\n")

consts = [5000, 0.0005, 20, 200, 0.0001]
# consts = [5000, 0.0005, 10, 200]
# consts = [5000, 0.001, 1, 200]

allowableError = 10

lastImprovement = 0
testCount = 0

# Function including 2nd degree equation
# consts = [5000, 0.0005, 20, 200, 0.0001, 0.0001, 0.0001]
# return( pow(2.0, (inPts+C[0])*C[1] )*C[2] + C[3] + inPts*C[4] + pow((inPts+C[6]), 2)*C[5])

def plotPow2Series(inPts, C):
    return( pow(2.0, (inPts+C[0])*C[1] )*C[2] + C[3] + inPts*C[4])

def getDataError(inPts, outPts, sigPts, constSet):
    testPts = plotPow2Series(inPts, constSet)
    errorSet = abs(testPts - outPts) * sigPts
    errorSet[ np.where(errorSet > allowableError)[0] ] = allowableError
    errorSet = pow( errorSet, 2)
    # errorSet = np.array_split( np.sort(errorSet), 3 )[0]
    error = sum(errorSet)

    if max(testPts) - min(testPts) < 20: error += allowableError*allowableError*len(testPts)
    return(error)

best_consts = deepcopy(consts)
best_error = getDataError(pos, frq, sig, best_consts)
test_consts = deepcopy(consts)

constHistory = [ [testCount] + deepcopy(best_consts) + [best_error]]
print(f"{best_consts}     {best_error}")

plt.ion()
fig, ax = plt.subplots(1)

# for ii in range(len(best_consts) +1):
#     ax[1].scatter(constHistory[-1][-1])



# print_iter = 0
def updatePlots():
    global best_consts
    global test_consts
    global testCount

    ax.cla()
    ax.scatter(pos, frq, alpha=sig*0.333, s=4)
    ax.plot(pos, plotPow2Series(pos, best_consts), label = str(testCount))
    # ax.plot(pos, plotPow2Series(pos, test_consts), label = str(lastImprovement))
    # ax.set_ylim(min(frq)-25, max(frq)+25)
    ax.set_ylim(min(frq)-25, 2000)
    ax.set_ylabel("Note Frequency (Hz)")
    ax.set_xlabel("Stepper Position (Steps)")
    # ax.legend()

    plt.draw()
    plt.pause(0.0001)
    # global print_iter
    # plt.savefig('tmp/dump/fig_'+str(print_iter)+'.png')
    # print_iter += 1

plt.ion()

updatePlots()



def newConsts():
    global best_consts
    global testCount

    halfTime = 150
    modFactor = halfTime/(testCount+halfTime)
    test_consts = deepcopy(best_consts)

    # for ii in range(len(test_consts)): test_consts[ii] *= (0.5 + r.random())/2
    changeSel = m.floor(r.random()*6.0)
    match changeSel:
        case 0:
            modInd = m.floor(r.random()*(len(test_consts) -1) +1)
            test_consts[modInd] *= (modFactor*(r.random() - 0.5) + 1.0)
        case 1:
            for ii in range(2):
                modInd = m.floor(r.random()*(len(test_consts) -1) +1)
                test_consts[modInd] *= (modFactor*(r.random() - 0.5) + 1.0)
        case 2:
            for ii in range(3):
                modInd = m.floor(r.random()*(len(test_consts) -1) +1)
                test_consts[modInd] *= (modFactor*(r.random() - 0.5) + 1.0)
        case 3:
            test_consts[1] *= modFactor*r.random() + 1.0
            test_consts[2] *= (1.0 - modFactor*r.random()/2)
        case 4:
            test_consts[1] *= (1.0 - modFactor*r.random()/2)
            test_consts[2] *= modFactor*r.random() + 1.0
        case 5:
            modAmount = (3*modFactor*(r.random() - 0.5) + 1.0)
            test_consts[1] *= modAmount
            test_consts[2] *= modAmount
            test_consts[3] *= modAmount

            
    if test_consts[0] < -1*min(pos): test_consts[0] = -1*min(pos)

    return(test_consts, changeSel)

while True:
    print(f"{testCount}\033[1A")
    testCount += 1
    test_consts, changeSel = newConsts()
    test_error = getDataError(pos, frq, sig, test_consts)

    if test_error < best_error:
        best_consts = test_consts
        best_error = test_error
        
        constHistory.append([testCount] + deepcopy(best_consts) + [best_error])

        constHist_zip = list(zip(*constHistory))
        
        # ax[1].cla()
        # for ii in range(1, len(constHist_zip)):
        #     fooData = np.array(constHist_zip[ii])
        #     ax[1].plot(constHist_zip[0], fooData/fooData[0], label="{:.4e}".format(fooData[-1]))
        # ax[1].legend()

        lastImprovement = testCount
        print(f"{testCount}   [", end='')
        for foo in best_consts: print("{:.4e}".format(foo), end=", ")
        print(f"]  {changeSel}   {best_error}")
    
        updatePlots()

    if testCount-lastImprovement > 250 or testCount > 2000: break

frq_match = plotPow2Series(pos, best_consts)
errorSet = abs(frq_match - frq)
errorSet = np.sort(errorSet)

errorSet = abs(frq_match - frq)

goodInds = np.where(errorSet <= allowableError)[0]
badInds = np.where(errorSet > allowableError)[0]









print("\n\n\nFINDING PITCH MATCHES\n")

pos_good = pos[goodInds]
frq_good = frq[goodInds]

note_pitches = np.array( [12543.85, 11839.82, 11175.3, 10548.08, 9956.06, 9397.27, 8869.84, 8372.02, 7902.13, 7458.62, 7040, 6644.88, 6271.93, 5919.91, 5587.65, 5274.04, 4978.03, 4698.64, 4434.92, 4186.01, 3951.07, 3729.31, 3520, 3322.44, 3135.96, 2959.96, 2793.83, 2637.02, 2489.02, 2349.32, 2217.46, 2093, 1975.53, 1864.66, 1760, 1661.22, 1567.98, 1479.98, 1396.91, 1318.51, 1244.51, 1174.66, 1108.73, 1046.5, 987.77, 932.33, 880, 830.61, 783.99, 739.99, 698.46, 659.26, 622.25, 587.33, 554.37, 523.25, 493.88, 466.16, 440, 415.3, 392, 369.99, 349.23, 329.63, 311.13, 293.66, 277.18, 261.63, 246.94, 233.08, 220, 207.65, 196, 185, 174.61, 164.81, 155.56, 146.83, 138.59, 130.81, 123.47, 116.54, 110, 103.83, 98, 92.5, 87.31, 82.41, 77.78, 73.42, 69.3, 65.41, 61.74, 58.27, 55, 51.91, 49, 46.25, 43.65, 41.2, 38.89, 36.71, 34.65, 32.7, 30.87, 29.14, 27.5, ] )
note_names = np.array( ["G9", "F#9/Gb9", "F9", "E9", "D#9/Eb9", "D9", "C#9/Db9", "C9", "B8", "A#8/Bb8", "A8", "G#8/Ab8", "G8", "F#8/Gb8", "F8", "E8", "D#8/Eb8", "D8", "C#8/Db8", "C8", "B7", "A#7/Bb7", "A7", "G#7/Ab7", "G7", "F#7/Gb7", "F7", "E7", "D#7/Eb7", "D7", "C#7/Db7", "C7", "B6", "A#6/Bb6", "A6", "G#6/Ab6", "G6", "F#6/Gb6", "F6", "E6", "D#6/Eb6", "D6", "C#6/Db6", "C6", "B5", "A#5/Bb5", "A5", "G#5/Ab5", "G5", "F#5/Gb5", "F5", "E5", "D#5/Eb5", "D5", "C#5/Db5", "C5", "B4", "A#4/Bb4", "A4", "G#4/Ab4", "G4", "F#4/Gb4", "F4", "E4", "D#4/Eb4", "D4", "C#4/Db4", "C4", "B3", "A#3/Bb3", "A3", "G#3/Ab3", "G3", "F#3/Gb3", "F3", "E3", "D#3/Eb3", "D3", "C#3/Db3", "C3", "B2", "A#2/Bb2", "A2", "G#2/Ab2", "G2", "F#2/Gb2", "F2", "E2", "D#2/Eb2", "D2", "C#2/Db2", "C2", "B1", "A#1/Bb1", "A1", "G#1/Ab1", "G1", "F#1/Gb1", "F1", "E1", "D#1/Eb1", "D1", "C#1/Db1", "C1", "B0", "A#0/Bb0", "A0", ] )
note_midiNumbers = np.array( [127, 126, 125, 124, 123, 122, 121, 120, 119, 118, 117, 116, 115, 114, 113, 112, 111, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21] )

print(f"note_pitches:{len(note_pitches)}")
print(f"note_names:{len(note_names)}")
print(f"note_midiNumbers:{len(note_midiNumbers)}")

outDict = {
    'name': [],
    'number': [],
    'pitch': [],
    'pos': [],
}

for midiInd in range(len(note_midiNumbers)):
    midiPitch = note_pitches[midiInd]
    if midiPitch < min(frq_good): continue
    if midiPitch > max(frq_good): continue
    
    prevInd = np.where(frq_good < midiPitch)[0][0]
    nextInd = np.where(frq_good > midiPitch)[0][-1]

    notePos = pos_good[prevInd] + (pos_good[nextInd] - pos_good[prevInd]) * (midiPitch - frq_good[prevInd]) / (frq_good[nextInd] - frq_good[prevInd])
    # notePos = pos[prevInd] + (pos[nextInd] - pos[prevInd]) * (midiPitch - frq[nextInd]) / (frq[nextInd] - frq[nextInd])

    # print(f"{pos[prevInd]} {pos[nextInd]}   -> {notePos}")

    outDict['name'].append(note_names[midiInd])
    outDict['number'].append(note_midiNumbers[midiInd])
    outDict['pitch'].append(midiPitch)
    outDict['pos'].append(notePos)

    # print("")
    # print(f"np.where(frq < midiPitch):{np.where(frq < midiPitch)[0]}")
    # print(f"np.where(frq > midiPitch):{np.where(frq > midiPitch)[0]}")

    print(f"Found note {note_names[midiInd]}   ({midiPitch}) at {notePos}    (between {pos[prevInd]} & {pos[nextInd]})")

print(f"Voice range is {min(outDict['name'])}->{max(outDict['name'])}   {min(outDict['number'])}->{max(outDict['number'])}")

for tag in outDict: outDict[tag] = np.array(outDict[tag])

# outputPickle_fileName = "MusicData/Instruments/" + instrumentName + "/noteRange.pkl"
# outPkl = open(outputPickle_fileName, 'wb')
# pkl.dump(outDict, outPkl)
# outPkl.close()

print("IS NOT SAVING CURRENTLY")

# print("Found Notes:")
# for ii in range(len(outDict['name'])):
#     print(f"   {outDict['name'][ii]} ({round(outDict['pitch'][ii], 1)}) at {outDict['pos'][ii]}")


ax.cla()
ax.plot(pos, frq_match)
ax.scatter(pos[goodInds], frq[goodInds], alpha=0.333*sig[goodInds])
ax.scatter(outDict['pos'], outDict['pitch'])
ax.scatter(pos[badInds], frq[badInds], alpha=0.333*sig[badInds])
ax.set_ylim(min(frq)-25, 2000)
ax.set_ylabel("Note Frequency (Hz)")
ax.set_xlabel("Stepper Position (Steps)")
plt.draw()
# plt.savefig('tmp/dump/fig_'+str(print_iter)+'.png')
plt.pause(1000.0)