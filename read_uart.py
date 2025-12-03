import serial

ser = serial.Serial('/dev/ttyAMA0', 115200)

while True:
    try:
        line = ser.readline().decode().strip()
        print("Received EMG:", line)
    except:
        pass
