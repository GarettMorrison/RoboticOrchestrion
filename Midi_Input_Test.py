import mido
import serial.tools.list_ports

noteDict = {
    48:0,
    50:1,
    52:2,
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
port = None
port = serial.Serial(SERIAL_PORT, baudrate=9600, timeout=0)#, rtscts=True)


with mido.open_input() as inport:
    for msg in inport:
        # print(msg)
        if msg.type == 'note_on':
            if msg.note in noteDict:
                if msg.velocity > 0:
                    port.write(int(noteDict[msg.note]).to_bytes(1, 'little', signed=False)) # Send byte indicating to trigger
                    # port.write(int(1).to_bytes(1, 'little', signed=False)) # Send byte indicating to trigger
                    print(f"ON {noteDict[msg.note]}")
                else:
                    port.write(int(noteDict[msg.note]+10).to_bytes(1, 'little', signed=False)) # Send byte indicating to trigger
                    # port.write(int(0).to_bytes(1, 'little', signed=False)) # Send byte indicating to trigger
                    print(f"OFF {noteDict[msg.note]}")