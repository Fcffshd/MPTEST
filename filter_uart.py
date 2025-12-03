import serial
import numpy as np
from scipy.signal import butter, lfilter

SERIAL_PORT = "/dev/ttyAMA0"
BAUD_RATE = 115200
FS = 1000   # Sampling rate 1 kHz

ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

# Bandpass 20–450 Hz
low = 20 / (FS/2)
high = 450 / (FS/2)
b, a = butter(4, [low, high], btype='band')

window = []

while True:
    line = ser.readline().decode().strip()
    voltage = float(line)

    window.append(voltage)
    if len(window) > 1000:
        window.pop(0)

    if len(window) > 50:
        filtered = lfilter(b, a, window)
        print("Filtered:", filtered[-1])
