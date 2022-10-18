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

peakData = loadPeaks(pklDict)
pos = np.array(peakData[peakIndex][0])
frq = np.array(peakData[peakIndex][1])
sig = np.array(peakData[peakIndex][2])/max(peakData[peakIndex][2])


minSig = 0.01
dropSet = np.where(sig < minSig)[0]
pos = np.delete(pos, dropSet, axis=0)
frq = np.delete(frq, dropSet, axis=0)
sig = np.delete(sig, dropSet, axis=0)
print(f"Dropped {len(dropSet)} points as sig < {minSig}")

minFreq = 100
dropSet = np.where(frq < minFreq)[0]
pos = np.delete(pos, dropSet, axis=0)
frq = np.delete(frq, dropSet, axis=0)
sig = np.delete(sig, dropSet, axis=0)
print(f"Dropped {len(dropSet)} points as frq < {minFreq}")

print(f"Final set len:{len(pos)}")





allowableError = 5


plt.ion()
fig, ax = plt.subplots(1)

best_consts = fitDataModel(pos, frq, sig, allowableError, ax)



frq_match = plotPow2Series(pos, best_consts)

outDict, goodInds, badInds = getMatches(pos, frq, sig, frq_match, allowableError, ax)








# outputPickle_fileName = "MusicData/Instruments/" + instrumentName + "/noteRange.pkl"
# outPkl = open(outputPickle_fileName, 'wb')
# pkl.dump(outDict, outPkl)
# outPkl.close()

print("IS NOT SAVING CURRENTLY")

# print("Found Notes:")
# for ii in range(len(outDict['name'])):
#     print(f"   {outDict['name'][ii]} ({round(outDict['pitch'][ii], 1)}) at {outDict['pos'][ii]}")



# plt.savefig('tmp/dump/fig_'+str(print_iter)+'.png')
plt.pause(1000.0)