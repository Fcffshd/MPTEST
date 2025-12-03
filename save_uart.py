import serial
import time
import csv
from datetime import datetime

SERIAL_PORT = "/dev/ttyAMA0"
BAUD_RATE = 115200

BUFFER_TIME = 5     # write to CSV every 5 seconds
buffer = []

csv_filename = "read_uart.csv"

# Create CSV file if doesn't exist
with open(csv_filename, "a", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp_ms", "voltage"])

ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

last_write = time.time()

while True:
    try:
        line = ser.readline().decode().strip()
        voltage = float(line)

        timestamp_ms = int(time.time() * 1000)
        buffer.append([timestamp_ms, voltage])

        if time.time() - last_write >= BUFFER_TIME:
            with open(csv_filename, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(buffer)
            buffer = []
            last_write = time.time()

    except Exception as e:
        print("Error:", e)
