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
from pyFuncs.DataProc import *



# Organ C Cap Pitches
pos = np.array([ 584, 494, 396, 396, 396, 359, 359, 308, 307, 307, 308, 297, 297, 296, 207, 207, 207, 584 ], dtype=float)
frq = np.array([ 275.6, 319.3, 390.6, 390.7, 399, 428, 429, 487, 490, 495, 498, 500.7, 503, 508, 680, 685, 686, 271], dtype=float)

# pos = np.array([ 207, 297, 396, 297, 396, 494, 584, 207, 396, 207], dtype=float)
# frq = np.array([ 680, 500.7, 399, 503, 390.7, 319.3, 275.6, 685, 390.6, 686 ], dtype=float)



sig = np.ones_like(frq)


# allowableError = 10

# plt.ion()
# fig, ax = plt.subplots(1)

# best_consts = fitDataModel(pos, frq, sig, allowableError, ax)

# frq_match = plotPow2Series(pos, best_consts)

# outDict, goodInds, badInds = getMatches(pos, frq, sig, frq_match, allowableError, ax)


def matchPolyFit(inData, fSet):
    outData = np.zeros_like(inData)

    for ii in range(len(fSet)):
        outData += fSet[::-1][ii]*pow(inData, ii)
    return(outData)

# frqLog2 = np.log2(frq)
# fSet = np.polyfit(pos, frqLog2, 3)


# pltPts = np.arange(min(pos), max(pos), 1)
# plt.scatter(pos, frq)
# plt.plot(pltPts, pow(2, matchPolyFit(pltPts, fSet)) )

# # plt.scatter(pos, frqLog2)
# # plt.plot(pltPts, matchPolyFit(pltPts, fSet))

# plt.show()





posLog2 = np.log2(pos)
fSet = np.polyfit(frq, posLog2, 3)



calcPitches = np.array(
    [349.23, 392, 440, 523.25, 587.33, 698.46], 
    dtype=float
    )
calcPosSet = pow(2, matchPolyFit(calcPitches, fSet))

for fooFrq, fooPos in zip(calcPitches, calcPosSet): print(f"Pitch {fooFrq} : {fooPos}")

pltPts = np.arange(min(frq), max(frq), 2)
plt.scatter(pos, frq, c='orange')
plt.scatter(calcPosSet, calcPitches, c='green')
plt.plot(pow(2, matchPolyFit(pltPts, fSet)), pltPts)
plt.xlabel("Pos")
plt.ylabel("Frq (Hz)")
plt.show()