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

plot_selection = 'peaks'
# plot_selection = 'heatmap'
# plot_selection = '3d'

readFilePath = 'MusicData/Instruments/Tenor/noteRec.pkl'
# readFilePath = 'MusicData/Instruments/Alto/noteRec.pkl'

# readFilePath = 'pickle/noteRec_'
# ii = 0
# while os.path.exists(readFilePath + str(ii) + '.pkl'): ii += 1 # Loop until filename ii is not taken
# readFilePath = readFilePath + str(ii-1) + '.pkl'


print(f'Opening {readFilePath}')

pklFile = open(readFilePath, 'rb')
pklDict = pkl.load(pklFile)
pklFile.close()

for foo in pklDict: print(foo)

Right = np.where(np.array(pklDict['solenoid_played']) == 'Right')[0]
Left = np.where(np.array(pklDict['solenoid_played']) == 'Left')[0]

calc_pitch = np.array( pklDict['calc_pitch'] )
calc_confidence = np.array( pklDict['calc_confidence'] )
stepper_position = np.array( pklDict['stepper_position'] )

RATE = pklDict['FS_RATE']




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
        pos += [fooPos for foo in foo_frqs]
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





if plot_selection == 'heatmap':
    FREQS_H = None
    AMPS_H = []
    for fooSig in pklDict['signal']:
        # freqs_h, amps_h = af.FFT_Both(RATE, fooSig)
        # freqs_h, amps_h = af.getHarmonic(RATE, fooSig, harmonicCount=2)
        freqs_h, amps_h = af.getHarmonic(RATE, fooSig)
        # freqs_h, amps_h = af.getHarmonic(RATE, fooSig, harmonicCount=4)
        FREQS_H = freqs_h
        AMPS_H.append(amps_h)

    fig, ax = plt.subplots()
    freqCutoff = 1000
    maxInd = np.where(FREQS_H < freqCutoff)[0][-1]
    ax.matshow([fooAmps[:maxInd]/sum(fooAmps[:maxInd]) for fooAmps in AMPS_H], aspect='auto')
    ax.set_xticks(FREQS_H[:maxInd][::m.floor(maxInd/15)][:-1])
    plt.show()

if plot_selection == 'peaks':
    peakData = loadPeaks(pklDict)
    for foo in peakData:
        plt.scatter(foo[0], foo[1], alpha=foo[2])
        
    outputPickle_fileName = "tmp/notePeaks.pkl"
    outPkl = open(outputPickle_fileName, 'wb')
    pkl.dump(peakData, outPkl)
    outPkl.close()

    plt.show()



if plot_selection == '3d':
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    
    peakData = loadPeaks(pklDict)
    for ii in range(len(peakData)):
        netIndex = sum([len(peakData[jj]) for jj in range(ii)])
        foo = peakData[ii]
        print(f"foo[0]   len:{len(foo[0])}")
        print(f"foo[1]   len:{len(foo[1])}")
        print(f"pklDict['solenoid_time'][netIndex:netIndex+len(peakData)]   len:{len(pklDict['solenoid_time'][netIndex:netIndex+len(peakData)])}")
        ax.scatter(
            foo[0], 
            foo[1],
            pklDict['solenoid_time'][netIndex:netIndex+len(foo[0])],
            alpha=np.array(foo[2])/5,
        )
    
    ax.set_xlabel("Stepper Position")
    ax.set_ylabel("Frequency (Hz)")
    ax.set_zlabel("Solenoid Strike Time")
    plt.show()


# plt.scatter(range(len(Right)), calc_pitch[Right], alpha = calc_confidence[Right] )
# plt.scatter(range(len(Left)), calc_pitch[Left], alpha = calc_confidence[Left] )


# plt.scatter(abs(stepper_position[Right]), calc_pitch[Right], alpha = calc_confidence[Right] )
# plt.scatter(abs(stepper_position[Left]), calc_pitch[Left], alpha = calc_confidence[Left] )



# plt.scatter(stepper_position[Right], calc_pitch[Right] )
# plt.scatter(stepper_position[Left], calc_pitch[Left] )

# plt.scatter(stepper_position[Right], calc_pitch[Right], alpha = calc_confidence[Right] )
# plt.scatter(stepper_position[Left], calc_pitch[Left], alpha = calc_confidence[Left] )


# plt.plot(range(len(Right)), calc_pitch[Right] )
# plt.plot(range(len(Left)), calc_pitch[Left] )

# plt.scatter(pklDict['calc_pitch'], pklDict['calc_confidence'])

plt.show()