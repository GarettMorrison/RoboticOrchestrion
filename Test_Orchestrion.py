


import pyFuncs.AudioFuncs as af
import pyFuncs.OrchestrionControl as oc
import pyFuncs.AudioManager as am

from matplotlib import pyplot as plt
import time
import math as m
import statistics as st
import numpy as np
from copy import deepcopy

if __name__ == '__main__':
    am.amSetup()
    oc.OC_init()
    
    # Open serial ports
    time.sleep(1) # Delay 1 second to allow Arduino to start up

    
    oc.setSolenoid('Tenor_Left', 6000)
    oc.setSolenoid('Tenor_Right', 6000)

    oc.setSolenoid('Alto_Left', 6000)
    oc.setSolenoid('Alto_Right', 6000)

    oc.setStepperDelay('Tenor', 8000)


    tmpDict = {
        'sigs':[],
        'tags':[],
        'RATE': 0,
    }
    

    # stepperPos = 0
    # factor = 10
    # prevDiff = 0
    # for TestIter in range(100):
    #     print(f"right:")
    #     right_pitch, right_confidence = am.measureAndSavePoint('Alto_Right')
    #     # print(f"   {round(right_pitch, 3)},    conf:{round(right_confidence, 5)}\n")

    #     print(f"left:")
    #     left_pitch, left_confidence = am.measureAndSavePoint('Alto_Left')
    #     # print(f"   {round(left_pitch, 3)},    conf:{round(left_confidence, 5)}\n")

    #     currDiff = right_pitch - left_pitch
        
    #     if currDiff * prevDiff > 0:
    #         factor *= 1.555
    #     else:
    #         factor /= 2

    #     stepperPos += currDiff * factor #/ abs(currDiff)

    #     prevDiff = currDiff

    #     if abs(currDiff) < 1.5:
    #         print(f"Calibration complete, diff is {str(currDiff)[:5].ljust(7)}")
    #         break
    #     print(f"currDiff:{str(currDiff)[:5].ljust(7)},   prevDiff:{str(prevDiff)[:5].ljust(7)}")
    #     print(f"Moved to {stepperPos}, factor:{str(factor)[:5].ljust(7)}\n")

    #     oc.moveToPos('Alto', stepperPos)
    
    # # import postProc
    
    # oc.zeroStepper('Alto', stepperPos)
    # exit()


    # while True:
    #     fooSolenoid = solenoids[ii%4]
    #     ii += 1
    #     rate, sig = recordStrike(1.5, fooSolenoid, playBack=False)
    #     # plt.cla()
    #     # plt.plot(sig)
    #     # plt.draw()
    #     # plt.pause(0.1)
    #     tmpDict['rate'] = rate
    #     tmpDict['sigs'].append(sig)
    #     tmpDict['tags'].append(fooSolenoid)

    #     tmpOut = open('pickle/sample_signals.pkl', 'wb')
    #     pkl.dump(tmpDict, tmpOut)
    #     tmpOut.close()

    # System quick check
    # while True:
        
    #     trigger('Tenor_Right')
    #     time.sleep(0.5)
    #     trigger('Tenor_Left')
    #     time.sleep(0.5)
    #     trigger('Alto_Right')
    #     time.sleep(0.5)
    #     trigger('Alto_Left')
    #     time.sleep(0.5)


    # System quick check
    for ii in range(4):
        oc.trigger('Tenor_Right')
        time.sleep(0.3)
        oc.trigger('Tenor_Right')
        time.sleep(0.6)
        oc.trigger('Alto_Right')
        time.sleep(0.3)
        oc.trigger('Alto_Left')
        time.sleep(0.3)
        oc.trigger('Tenor_Left')
        time.sleep(0.3)
        oc.trigger('Alto_Right')
        time.sleep(0.3)
        oc.trigger('Alto_Left')
        time.sleep(0.3)
        
    for ii in range(8):
        oc.trigger('Tenor_Right')
        time.sleep(0.3)
        oc.trigger('Tenor_Right')
        time.sleep(0.6)
        oc.trigger('Alto_Right')
        time.sleep(0.3)
        oc.trigger('Alto_Left')
        oc.trigger('Tenor_Right')
        time.sleep(0.3)
        oc.trigger('Tenor_Left')
        time.sleep(0.3)
        oc.trigger('Alto_Right')
        oc.trigger('Tenor_Right')
        time.sleep(0.3)
        oc.trigger('Alto_Left')
        time.sleep(0.3)

        # trigger('Alto_Left')
        # moveToPos('Tenor', 400)
        
        # trigger('Alto_Left')
        # moveToPos('Tenor', 0)
        
        # trigger('Alto_Left')
        # moveToPos('Tenor', -400)
        
        # trigger('Alto_Left')
        # moveToPos('Tenor', 0)






    SMOOTH_POINTS = 2
    FREQS_avg = smoothPts(FREQS, SMOOTH_POINTS)

    stepperPos = 0
    while True:
        # for fooSolenoid in solenoidData:
        #     fftAmps, measureSuccess = measureAndSavePoint(fooSolenoid)
        #     print( f" {pklDict['voice_played'][-1]}_{pklDict['solenoid_played'][-1]} : {round(pklDict['maxFreq'][-1], 1)} confidence: {round(pklDict['confidenceRatio'][-1], 2)} ")
        
        setSolenoid('Alto_Left', r.randint(5000, 10000))
        fooSolenoid = 'Alto_Left'
        fftAmps, measureSuccess = measureAndSavePoint(fooSolenoid)
        # print( f" {pklDict['voice_played'][-1]}_{pklDict['solenoid_played'][-1]} : {round(pklDict['maxFreq'][-1], 1)}")
        leftPitch = pklDict['maxFreq'][-1]

        setSolenoid('Alto_Right',  r.randint(5000, 10000))
        fooSolenoid = 'Alto_Right'
        fftAmps, measureSuccess = measureAndSavePoint(fooSolenoid, clearIfPlot = False)
        # print( f" {pklDict['voice_played'][-1]}_{pklDict['solenoid_played'][-1]} : {round(pklDict['maxFreq'][-1], 1)}")
        rightPitch = pklDict['maxFreq'][-1]
        
        freqDiff = rightPitch - leftPitch 
        calcMove = freqDiff/0.05769
        if calcMove > 600: calcMove = 600
        if calcMove < -600: calcMove = -600

        stepperPos += calcMove
        print(f'leftPitch:{round(leftPitch, 2)}   rightPitch:{round(rightPitch, 2)}   calcMove:{calcMove}   stepperPos:{stepperPos}')
        moveToPos('Alto', stepperPos)
        
        
        
        # measurementTaken = False
        # while not measurementTaken:
        #     ampsSorted = sorted(fftAmps)
        #     # print(f'No peak measured ratio is {ampsSorted[-1]/ampsSorted[-2]}')


        #     fftAmpsAvg = smoothPts(fftAmps, SMOOTH_POINTS)

        #     maxAmp = max(fftAmpsAvg)
        #     maxIndex = np.where(fftAmpsAvg == maxAmp)[0][0]
        #     measuredFreq = FREQS_avg[maxIndex]

        #     print(f'{round(measuredFreq, 3)}')
            
            # maxFreqInd = np.where(FREQS_avg > 2000)[0][0]
            # minFreqInd = np.where(FREQS_avg > 0)[0][0]

            # plt.cla()
            # plt.plot(FREQS_avg, fftAmpsAvg)
            # plt.scatter([measuredFreq], [maxAmp], color='red')
            # plt.xticks(range(len(FREQS_avg))[::500], FREQS_avg[::500])
            # plt.xlim(0, 2000)
            # plt.draw()
            # plt.pause(0.1)











    # # maxFreqInd = np.where(FREQS > 800)[0][0]
    # # minFreqInd = np.where(FREQS > 250)[0][0]
    # print(f'maxFreqInd:{maxFreqInd}    minFreqInd:{minFreqInd}')

    # # Find stepper pos for specific point
    # print('measuredFreq,   freqDiff,   nextPos')
    # def smoothPts(inPts, ptCount): return( [sum(inPts[ii:ii+ptCount])/ptCount for ii in range(len(inPts) - ptCount)] )

    # FREQS_avg = smoothPts(FREQS, 1)
    # targetFreq = 360
    
    # while True:
    #     measureAndSavePoint()
    #     fftAvg = smoothPts(pklDict['fftAmps'][-1], 1)

 
    #     maxAmp = max(fftAvg[minFreqInd:maxFreqInd])
    #     maxIndex = fftAvg.index(maxAmp)
    #     measuredFreq = FREQS_avg[maxIndex]
        
    #     freqDiff = targetFreq - measuredFreq
    #     calcMove = freqDiff/0.05769
    #     if calcMove > 600: calcMove = 600
    #     if calcMove < -600: calcMove = -600

    #     nextPos = stepperPos + calcMove



    #     plt.cla()
    #     plt.plot(FREQS_avg, fftAvg)
    #     plt.scatter([measuredFreq], [maxAmp], color='red')
    #     # plt.xticks(range(len(FREQS_avg))[::500], FREQS_avg[::500])
    #     plt.xlim(FREQS_avg[minFreqInd], FREQS_avg[maxFreqInd])
    #     plt.draw()
    #     plt.pause(0.05)


    #     # if maxIndex > maxFreqInd or maxIndex < minFreqInd:
    #     #     print(f'{round(measuredFreq, 1)}   not in range')
    #     #     continue
        
    #     if abs(freqDiff) < 1.5:
    #         print(f'{round(measuredFreq, 1)}   found note!')
    #         break
        
    #     elif maxAmp < 3*st.median(fftAvg[minFreqInd:maxFreqInd]):
    #         print(f'{round(measuredFreq, 1)}, at {round(maxIndex)}   no spike found')
        
    #     else:
    #         print(f'{round(measuredFreq, 1)} at {round(maxIndex)}   diff is {round(freqDiff, 1)}   moving to {nextPos}!')
    #         moveToPos(nextPos)


    #     # print(f'maxIndex:{maxIndex}    measuredFreq:{measuredFreq}')


    #     # print(f'{measuredFreq},   {freqDiff},   {nextPos}')

    # setSolenoid(14000)

    # # trigger()
    # # time.sleep(0.4)
    # # for foo in range(3):
    # #     trigger()
    # #     time.sleep(0.2)

    # for foo in [1,1,1,1,0,1,1,0,1,1]:    
    #     if foo: trigger()
    #     time.sleep(0.2)

    
    # exit()

    # # Test range of points

    # # valSet = [5000, 60000] # Value range for solenoid striker timing
    # valSet = [-2500, 2500]
    # ptCount = 0
    # runCount = 0
    # while True:
    #     print(f'runCount:{runCount}')
    #     newValSet = []
    #     for ii in range( len(valSet) -1 ):
    #         testVal = sum(valSet[ii:ii+2])/2
    #         newValSet.append(valSet[ii])
    #         newValSet.append(testVal)

    #         # setSolenoid(testVal) # Test different strike durations
    #         moveToPos(testVal) # Test different positions
    #         print(f'   {ptCount} : {testVal}')
    #         measureAndSavePoint()
    #         # livePlot()
    #         ptCount += 1

    #     newValSet.append(valSet[-1])
    #     valSet = newValSet
    #     runCount += 1
    

    # # print(maxFreqDisplay)
    # # print(maxFreqDisplay[0][0])

    # # plt.scatter(pklDict['solenoid_time'], pklDict['maxFreq_Amp_Approx'])


    # for foo in pklDict['fftAmps']: 
    #     print(F'{FREQS[np.where(amps == max(amps))[0][0]]} : {max(amps)}')
    #     plt.plot(FREQS, foo)
    # plt.scatter(pklDict['maxFreq'], pklDict['maxFreq_Amp_Approx'])

    # maxFreqDisplay = np.where(freqs > 2050)
    # plt.xlim(0, maxFreqDisplay[0][0])
    # plt.show()



