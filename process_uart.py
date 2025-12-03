import serial
import numpy as np
import time

SERIAL_PORT = "/dev/ttyAMA0"
BAUD_RATE = 115200

ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

window = []

WINDOW_SIZE = 200   # 200 samples = 200 ms @ 1kHz

while True:
    line = ser.readline().decode().strip()
    voltage = float(line)

    window.append(voltage)
    if len(window) > WINDOW_SIZE:
        window.pop(0)

    # Example: RMS envelope
    rms_value = np.sqrt(np.mean(np.square(window)))

    print("EMG RMS:", rms_value)
