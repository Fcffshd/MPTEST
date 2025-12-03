import serial
import matplotlib.pyplot as plt
import collections

SERIAL_PORT = '/dev/serial0'
BAUD_RATE = 115200

ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

window = collections.deque(maxlen=1000)

plt.ion()
fig, ax = plt.subplots()
line, = ax.plot([], [])
ax.set_ylim(0, 3.3)
ax.set_xlim(0, 1000)
ax.set_title("Real-Time EMG Voltage Stream")
ax.set_xlabel("Samples (last 1000)")
ax.set_ylabel("Voltage (V)")

while True:
    try:
        line_str = ser.readline().decode().strip()
        voltage = float(line_str)
        window.append(voltage)

        line.set_data(range(len(window)), list(window))
        plt.pause(0.001)

    except Exception as e:
        print("Error:", e)
