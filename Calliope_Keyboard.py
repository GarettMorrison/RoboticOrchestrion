import mido
import serial.tools.list_ports


noteDict = {
    48:0,
    50:1,
    62:2,
    53:3,
    55:4,
    57:5,
    59:6,
    60:7,
}


ports = serial.tools.list_ports.comports()
print("\nThe following ports are available:")
for port, desc, hwid in sorted(ports): print("{}: {} [{}]".format(port, desc, hwid))

SERIAL_PORT = 'COM3'
SERIAL_BAUD = 9600
# SERIAL_BAUD = 19200
port = None
port = serial.Serial(SERIAL_PORT, baudrate=SERIAL_BAUD, timeout=0)#, rtscts=True)

checkSum = b'\x00'
def sendCommandByte(val, byteCount):
    global checkSum
    outByte = int(val).to_bytes(byteCount, 'little', signed=False)
    port.write(outByte)
    checkSum += outByte

def endCommand():
    global checkSum
    checkSum = int(sum(checkSum)%256).to_bytes(1, 'little', signed=False) # Solve checksum
    port.write(checkSum)
    checkSum = b'\x00'
    port.flush()



with mido.open_input() as inport:
    for msg in inport:
        if msg.type == 'note_on' and msg.velocity > 0: print(f"{msg.note}")
        # print(msg)
        if msg.type == 'note_on' and msg.note in noteDict:
            if msg.velocity > 0:
                noteCommand = 0
            else:
                noteCommand = 1

            sendCommandByte(1, 1)
            sendCommandByte(noteCommand, 1)
            sendCommandByte(noteDict[msg.note], 1)
            endCommand()

        while port.in_waiting:  # Or: while port.inWaiting():
            print(f"ser read:  {int.from_bytes(port.read(), 'little')}")