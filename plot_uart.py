import serial
import matplotlib.pyplot as plt
import collections

# UART settings
SERIAL_PORT = '/dev/serial0'   # UART0 RX (GPIO15)
BAUD_RATE = 115200

# Open serial port
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

# Rolling data window (1000 samples)
window = collections.deque(maxlen=1000)

plt.ion()
fig, ax = plt.subplots()

while True:
    try:
        # Read a line of UART text
        line = ser.readline().decode().strip()
        voltage = float(line)  # convert string → float

        # Store latest value
        window.append(voltage)

        # Plot
        ax.clear()
        ax.plot(list(window))
        ax.set_ylim(0, 3.3)  # ESP8266 A0 range (0–3.3v)
        ax.set_title("Real-Time EMG Voltage Stream")
        ax.set_xlabel("Samples (last 1000)")
        ax.set_ylabel("Voltage (V)")

        plt.pause(0.001)

    except Exception as e:
        print("Error:", e)
