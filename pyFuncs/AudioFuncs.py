from numpy import sign
import pyaudio
import wave

import math as m
import scipy
import scipy.fftpack
import numpy as np
from copy import deepcopy

import scipy.io.wavfile as wavfile
from scipy.signal import find_peaks

from matplotlib import pyplot as plt

### Getting inputs

def recordAudio(recordTime =1, outputFile = '', playBack = False):
    
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    print(f'RATE:{RATE}')

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    # print("* recording")

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
        # print(ii)
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



def playAudio(signal):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    play = pyaudio.PyAudio()
    playStream = play.open(
        rate=44100,
        format=pyaudio.paInt16,
        channels=1,
        output=True,
    )
    CHUNK = 1024
    ii = 0

    print(signal)

    data=bytes(signal[:CHUNK] )
    while data != b'':
        playStream.write(data)
        ii+=1
        data = bytes( signal['audio'][1][CHUNK*(ii-1):CHUNK*ii] )



def loadWav(fileName):
    fileShort = fileName.split("/")[-1] #Title for file
    fs_rate, signal = wavfile.read(fileName) #Read file

    l_audio = len(signal.shape)
    if l_audio == 2:
        signal = signal.sum(axis=1) / 2

    return(fs_rate, signal)


### Taking FFTs
def getFFT(signal):
    midpoint = m.floor((len(signal)-1)/2)
    FFT = abs(scipy.fft.fft(signal))
    return(abs(FFT)[:midpoint])

def getFFT_Freqs(fs_rate, signal):
    midpoint = m.floor((len(signal)-1)/2)
    freqs = scipy.fftpack.fftfreq(len(signal)) * fs_rate
    return(freqs[:midpoint])

def FFT_Both(fs_rate, signal): 
    signal = signal*np.hanning(len(signal))
    return(getFFT_Freqs(fs_rate, signal), getFFT(signal))

def FFT_Peaks(FFT_Frqs, FFT_Data): 
    # freqs = getFFT_Freqs(fs_rate, signal)
    # amps = getFFT(signal)
    peakInds = find_peaks(FFT_Data, distance=len(FFT_Data)/20)[0]
    return(FFT_Frqs[peakInds], FFT_Data[peakInds])
    
def getHarmonic(RATE, sig, prevPitch=0.0, harmonicCount = 3):
    sig = sig*np.hanning(len(sig))
    
    freqs, amps = FFT_Both(RATE, sig)
    amps[np.where(freqs < 90)] = 0
    amps_orig = deepcopy(amps)

    amps_harmonics = np.ones_like(amps)

    harmonicSums = np.zeros_like(amps)
    
    # print('\n\n\n')
    for jj in range(1, harmonicCount+1): # Only first and second harmonic
        hps_len = int(np.ceil(len(amps) / jj))
        amps_harmonics[:hps_len] *= amps_orig[::jj]  # multiply every i element

        harmonicSums += (amps_harmonics/sum(amps_harmonics))
    
    # return(freqs, harmonicSums)
    return(freqs, amps_harmonics)


### Processing FFT data

def maxIndex(npArr): return(np.where(npArr == max(npArr))[0][0])
def nearestIndex(inVal, npArr): return((np.abs(npArr - inVal)).argmin())

def getFreq(FFT_Frqs, FFT_Data):
    peakFreq = FFT_Frqs[maxIndex(FFT_Data)]

    ptRange = 1
    pAvg_bot = maxIndex(FFT_Data) - ptRange
    pAvg_top = maxIndex(FFT_Data) + ptRange

    pAvg_top += 1
    pitchVal = 0
    for ii in range(pAvg_bot, pAvg_top):
        pitchVal += FFT_Data[ii]*FFT_Frqs[ii]
    pitchVal /= sum(FFT_Data[pAvg_bot:pAvg_top])

    return(pitchVal, peakFreq)

def freqFromSignal(fs_rate, signal): 
    FFT_Frqs, FFT_Data = FFT_Both(fs_rate, signal)
    return(getFreq(FFT_Frqs, FFT_Data))



# def FFT_Peaks(FFT_Frqs, FFT_Data):
#     maxInd = maxIndex(FFT_Data)
#     minSigVal = FFT_Data[maxInd]/4

#     peakFreqs = []
#     peakAmps = []

#     while True:
#         maxInd = maxIndex(FFT_Data)
#         maxVal = FFT_Data[maxInd]
#         if maxVal < minSigVal: break

#         peakFreqs.append(FFT_Frqs[maxInd])
#         peakAmps.append(FFT_Data[maxInd])

#         FFT_Data[maxInd] = 0

#         for ii in range(len(FFT_Data)):
#             # if FFT_Data[ii] < maxVal* (1 - abs(FFT_Frqs[ii] - FFT_Frqs[maxInd])/100):
#             if FFT_Data[ii] < maxVal* (1 - abs(ii - maxInd)/200):
#                 FFT_Data[ii] = 0
    
#     return(peakFreqs, peakAmps)