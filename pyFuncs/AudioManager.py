from cmath import inf
import pyFuncs.AudioFuncs as af
import pyFuncs.OrchestrionControl as oc

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


AUDIO_REC_TIME = 1 # Time to record in seconds
STRIKE_DELAY = 0 #AUDIO_REC_TIME/1.5
DISPLAY_FEEDBACK = False


outputFilePath = ''
pklDict = {}

def amSetup():
    global pklDict
    global outputFilePath
    # Get new file to save points to
    outputFilePath = 'pickle/noteRec_'
    ii = 0
    while os.path.exists(outputFilePath + str(ii) + '.pkl'): ii += 1 # Loop until filename ii is not taken
    outputFilePath = outputFilePath + str(ii) + '.pkl'
    print('Saving to ' + outputFilePath)
    tmpFile = open(outputFilePath, 'w')
    tmpFile.close()
    
    # Set up multiprocessing to record while playing

    # Set up recording program
    print('Recording Background Noise!')
    if DISPLAY_FEEDBACK: FS_RATE, baseSignal = recordStrike(AUDIO_REC_TIME, '', False)
    else: FS_RATE, baseSignal = recordStrike(AUDIO_REC_TIME, '')

    print(f'FS_RATE:{FS_RATE}')

    freqs, amps = af.FFT_Both(FS_RATE, baseSignal)
    FREQS = deepcopy(freqs)
    amps_BackGround = deepcopy(amps)

    pklDict = {
        'FREQS': FREQS,
        'FS_RATE':FS_RATE,
        'AUDIO_REC_TIME':AUDIO_REC_TIME,

        'voice_played':[], 
        'solenoid_played':[], 
        'solenoid_time':[], 
        'stepper_duration':[], 
        'stepper_position':[], 
        'stepper_previous_pos':[], 
        'signal':[], 
        'calc_pitch':[], 
        'calc_confidence':[], 
        
    }



# Record audio and strike
def recordStrike(recordTime, strikeSel, playBack=False): 
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    # RATE = 44100
    RATE = 48000

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    # print("* recording")

    if strikeSel != '':
        oc.trigger(strikeSel)

    frames = []

    for i in range(0, int(RATE / CHUNK * recordTime)):
        data = stream.read(CHUNK)
        frames.append(data)

    # print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    # Process frames
    frames = b''.join(frames)
    signal = []
    for ii in range(0, len(frames), 2):
        signal.append(int.from_bytes(frames[ii:ii+2], "little", signed=True))

    if playBack:
        play = pyaudio.PyAudio()
        playStream = play.open(
            rate=RATE,
            format=pyaudio.paInt16,
            channels=CHANNELS,
            output=True,
        )
        
        playStream.write(frames)

    return(RATE, signal)
    



# Save data to pickle
def savePickle(filepath, saveDict):
    pklFile = open(filepath, 'wb')
    pkl.dump(saveDict, pklFile)
    pklFile.close()
    
def smoothPts(inPts, ptCount): return( np.array([sum(inPts[ii:ii+ptCount])/ptCount for ii in range(len(inPts) - ptCount)]) )


    


def getFreqAndConf(sig, RATE, prevPitch=0.0, ax = None):
    if ax is None: doPrint = False
    else: doPrint = True
    sig = sig*np.hanning(len(sig))
    
    freqs, amps = af.FFT_Both(RATE, sig)
    amps[np.where(freqs < 90)] = 0
    amps_orig = deepcopy(amps)

    amps_harmonics = np.ones_like(amps)

    bestFreq = 0.0
    bestConf = 0.0
    bestHarm = 0
    
    for jj in range(1, 4): # Only first and second harmonic
        hps_len = int(np.ceil(len(amps) / jj))
        amps_harmonics[:hps_len] *= amps_orig[::jj]  # multiply every i element

        if doPrint: 
            ax[jj-1].plot(freqs, amps_harmonics/(max(amps_harmonics)))
            ax[jj-1].set_xlim(60, 1500)
    
    if prevPitch > 0.01:
        amps_harmonics = amps_harmonics/(abs(freqs - prevPitch) + 10)
    amps = deepcopy(amps_harmonics)

    # Get peak
    peakIdx = np.where(amps == max(amps))[0][0]
    peakAmps = max(amps)

    # Get second highest peak
    prevAmp = peakAmps
    for ii in range(peakIdx, len(amps)):
        if amps[ii] > prevAmp: break # Slope changes
        prevAmp = amps[ii]
        amps[ii] = 0
        
    prevAmp = peakAmps
    for ii in range(peakIdx, -1, -1):
        if amps[ii] > prevAmp: break # Slope changes
        prevAmp = amps[ii]
        amps[ii] = 0

    peak_2nd = max(amps)

    confidence = (1 - peak_2nd/peakAmps)

# if confidence > bestConf and jj > 1:
# if confidence > bestConf and jj == 3:

    # # Test code to drop an octave if it makes sense
    # bestFreq = freqs[peakIdx]

    # divCount = 2
    # while True:
    #     checkIdx = np.argsort( abs(freqs - bestFreq/divCount) )[0]
    #     # print(f"{peakIdx} : {checkIdx}")
    #     octavePeak = amps_harmonics[checkIdx]

    #     if octavePeak*8 > peakAmps:
    #         # if not doPrint: print('DROPPING OCTAVE')
    #         peakIdx = checkIdx

    #         divCount *= 2
    #     else:
    #         break

    
    bestFreq = freqs[peakIdx]
    bestConf = confidence
    # bestHarm = jj
    # bestIdx = peakIdx
    
    # if doPrint: plt.show()

    # bestAmps = deepcopy(amps_harmonics)

    # peakVal = bestAmps[bestIdx]
    # peakFreq = freqs[bestIdx]
    # peakVal_2nd = 0
    # peakFreq_2nd = 0
    # if bestAmps[bestIdx +1] > bestAmps[bestIdx -1]:
    #     peakVal_2nd = bestAmps[bestIdx +1]
    #     peakFreq_2nd = freqs[bestIdx +1]
    # else:
    #     peakVal_2nd = bestAmps[bestIdx -1]
    #     peakFreq_2nd = freqs[bestIdx -1]
    
    # # freqMod = (peakFreq_2nd - peakFreq) * (peakVal - peakVal_2nd)/(peakVal_2nd + peakVal)/2 
    # freqMod = (peakFreq_2nd - peakFreq) * ( 1 - pow( (peakVal - peakVal_2nd)/( (peakVal_2nd + peakVal)) ,2)) /1
    
    # # if abs(freqMod) > 5:
    # #     print(f"{bestFreq} : {peakFreq_2nd} | {freqs[bestIdx +1]}")
    # #     print(f"{bestAmps[bestIdx +1] > bestAmps[bestIdx -1]}")
    # #     print(f"len: {len(sig)}")
    # #     print(f"rate:{RATE}")
    # #     print(f"\n\n")

    # bestFreq += freqMod

    # print( freqMod  )
    return( bestFreq, bestConf  )

def clpr(inVal, max, len): return( str(inVal)[:max].ljust(len) )



def calcPitch_1SecCalibrated(sig, RATE, prevPitch = 0.0, name=''):
    sig = sig[5000:]
    dataLims = [2897, 2971, 3067, 3169, 3253, 3329]
    # dataLims = [2897, 2971, 3067, 3169]
    testCount = len(dataLims)

    freqSet = np.zeros(testCount)
    confSet = np.zeros(testCount)
    for ii in range(testCount):
        freqSet[ii], confSet[ii] = getFreqAndConf(sig[:dataLims[ii]], RATE, prevPitch=prevPitch)
    
    # sortIdx = np.argsort(freqSet)#[1:-1]
    # print(f"\n{freqSet[sortIdx]}")
    
    sortIdx = np.argsort(freqSet)[1:-1]
    # sortIdx = np.argsort(freqSet)
    # print(f"{freqSet[sortIdx]}")

    netFreq = sum(freqSet[sortIdx] * confSet[sortIdx])/(sum(confSet[sortIdx]))
    netConf = st.median(confSet[sortIdx]) # second highest confidence

    if st.stdev(freqSet[sortIdx]) > 6:
        netConf = -1
        
    

    if netConf > 0.6:
        print(f"   {name}   ", end='')
        print(f"{clpr(netFreq, 5, 7)}:{clpr(netConf, 5, 7)}  {clpr(st.stdev(freqSet[sortIdx]), 5, 7)}  |  ", end='')

        # for ii in range(testCount): print(f"{clpr(freqSet[sortIdx][ii], 5, 7)}:{clpr(confSet[sortIdx][ii], 5, 7)}  ", end='')
        
        for ii in range(testCount-2): print(f"{clpr(freqSet[sortIdx][ii], 5, 7)}:{clpr(confSet[sortIdx][ii], 5, 7)}  ", end='')
        sortIdx = np.argsort(freqSet)[1:-1]
        print(f"|  drop:{clpr(freqSet[sortIdx][0], 5, 7)}:{clpr(confSet[sortIdx][0], 5, 7)} & {clpr(freqSet[sortIdx][-1], 5, 7)}:{clpr(confSet[sortIdx][-1], 5, 7)}")
        # print('')

    return( netFreq, netConf  )






# Play note, record audio, process audio, save to pickle
def measureAndSavePoint(solSel, prevPitch = 0.0, clearIfPlot = True):
    global pklDict
    
    if DISPLAY_FEEDBACK: rate, signal = recordStrike(AUDIO_REC_TIME, solSel, True)
    else: rate, signal = recordStrike(AUDIO_REC_TIME, solSel)
    pitch, confidence = calcPitch_1SecCalibrated(signal, rate, prevPitch = prevPitch, name=solSel)

    # confidenceReq = 0.6
    # # confidenceReq = 0.65

    # while confidence < confidenceReq:
    #     # print(f"   {pitch},    conf:{confidence}")

    #     if DISPLAY_FEEDBACK: rate, signal = recordStrike(AUDIO_REC_TIME, solSel, True)
    #     else: rate, signal = recordStrike(AUDIO_REC_TIME, solSel)

    #     pitch, confidence = calcPitch_1SecCalibrated(signal, rate, prevPitch = prevPitch, name=solSel)

    
    stepperName = solSel.split('_')[0]
    pklDict['voice_played'].append(stepperName)
    pklDict['solenoid_played'].append(solSel.split('_')[1])

    pklDict['solenoid_time'].append(oc.solenoidData[solSel]['duration'])

    pklDict['stepper_duration'].append(oc.stepperData[stepperName]['stepDelay'])
    pklDict['stepper_position'].append(oc.stepperData[stepperName]['pos'])
    pklDict['stepper_previous_pos'].append(oc.stepperData[stepperName]['prevPos'])

    pklDict['signal'].append(signal)
    pklDict['calc_pitch'].append(pitch)
    pklDict['calc_confidence'].append(confidence)

    global outputFilePath
    savePickle(outputFilePath, pklDict)

    return(pitch, confidence)

     
def findNote(stringName, solName, targNote, prevPitch=0.0, stepperRange=None):
    stepperPos = oc.stepperData[stringName]['pos']
    factor = 10
    prevDiff = 0
    
    prevPitch, confidence = measureAndSavePoint(solName, prevPitch=prevPitch)
    lowChangeCount = 0
    lastWasWeird = 1.0
    hasCrossed = False

    for TestIter in range(40):
        # print(f"{stringName} right:")
        pitch, confidence = measureAndSavePoint(solName, prevPitch=prevPitch)
        
        if (targNote -pitch) * (targNote-prevPitch) > 0:
            if hasCrossed: factor *= 1.222
            else: factor *= 1.555
        else:
            hasCrossed = True
            factor /= 2

        pitchChange = abs(pitch - prevPitch)

        # adjustmentList = [-1000, round(currDiff * factor), 1000]
        # print(adjustmentList.sort() )
        currDiff = targNote -pitch

        if pitch/prevPitch > 1.6 or pitch/prevPitch < 0.7:
            if pitch/lastWasWeird > 1.6 or pitch/lastWasWeird < 0.7:
                lastWasWeird = pitch
                continue
            
        lastWasWeird = 1.0

        if 'Left' in solName:
            stepperPos += sorted( [-1000, round((currDiff) * factor), 1000] )[1] #/ abs(currDiff)
        else:
            stepperPos += sorted( [-1000, round(-1*(currDiff) * factor), 1000] )[1] #/ abs(currDiff)


        if abs(currDiff)/targNote < 0.006:
            print(f"{targNote} Hz found at {stepperPos}, diff is {str(currDiff)[:5].ljust(7)}")
            return(True)

        # print(f"currDiff:{str(currDiff)[:5].ljust(7)},   prevDiff:{str(prevDiff)[:5].ljust(7)}")
        # print(f"Moved to {stepperPos}, factor:{str(factor)[:5].ljust(7)}\n")
        
        if stepperRange != None:
            if stepperPos < stepperRange[0] or stepperPos > stepperRange[1]:
                oc.moveToPos(stringName, 0)
                return(False)

        oc.moveToPos(stringName, stepperPos)
        
        prevPitch = pitch
    print('Too many steps taken, cancelling')
    return(False)

     
def zeroString(stringName):
    stepperPos = 0
    factor = 10
    prevDiff = 0
    for TestIter in range(100):
        # print(f"{stringName} right:")
        right_pitch, right_confidence = measureAndSavePoint(stringName + '_Right')
        time.sleep(1)
        # print(f"   {round(right_pitch, 3)},    conf:{round(right_confidence, 5)}\n")

        # print(f"{stringName} left:")
        left_pitch, left_confidence = measureAndSavePoint(stringName + '_Left')
        # print(f"   {round(left_pitch, 3)},    conf:{round(left_confidence, 5)}\n")

        currDiff = right_pitch - left_pitch
        
        if currDiff * prevDiff > 0:
            factor *= 1.555
        else:
            factor /= 2


        # adjustmentList = [-1000, round(currDiff * factor), 1000]
        # print(adjustmentList.sort() )

        stepperPos += sorted( [-500, round(currDiff * factor), 500] )[1] #/ abs(currDiff)

        prevDiff = currDiff

        if abs(currDiff) < 3:
            print(f"{stringName} calibration complete, diff is {str(currDiff)[:5].ljust(7)}")
            break
        print(f"currDiff:{str(currDiff)[:5].ljust(7)},   prevDiff:{str(prevDiff)[:5].ljust(7)}")
        print(f"Moved to {stepperPos}, factor:{str(factor)[:5].ljust(7)}\n")

        oc.moveToPos(stringName, stepperPos)
    
    # import postProc
    
    oc.zeroStepper(stringName)
