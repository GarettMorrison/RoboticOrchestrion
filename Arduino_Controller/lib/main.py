import AudioFuncs as af

from matplotlib import pyplot as plt

import serial
import sys
import time

# fs_rate, signal = af.loadWav("d:/Code/Audio_Py/data/bottle.wav")


port = serial.Serial('COM11', baudrate=19200, timeout=0)#, rtscts=True)
time.sleep(1)


# for ii in range(1,255, 4):
#     port.write(int(ii).to_bytes(1, "big"))

#     # time.sleep(0.2)

#     fs_rate, signal = af.recordAudio(1)

#     # port.write(int(0).to_bytes(1, "big"))

#     print(str(ii) + ', ' + str(af.freqFromSignal(fs_rate, signal)[0]))

# port.write(int(0).to_bytes(1, "big"))


while(True):
    sendVal = input("Value to send:")
    port.write(int(sendVal).to_bytes(1, "big"))
    time.sleep(0.2)
    print("Returned:")
    print(port.read(1))

# print(returnCode)