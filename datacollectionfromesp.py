import serial
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# --- Configuration ---
PORT = "COM4"
BAUD = 115200
EXCEL_FILE = "esp32_log.xlsx"
SAMPLES = 200         

# --- Initialize serial ---
ser = serial.Serial(PORT, BAUD, timeout=1)
records = []

print("Collecting data from ESP32...")

while len(records) < SAMPLES:
    line = ser.readline().decode(errors="ignore").strip()
    if not line or "sample" in line:
        continue
    try:
        sample, raw, mv = line.split(",")
        voltage_v = float(mv) / 1000.0
        timestamp = datetime.now().isoformat(timespec="milliseconds")
        records.append({
            "Timestamp": timestamp,
            "Sample": int(sample),
            "Voltage (V)": voltage_v
        })
        print(f"{timestamp}: {voltage_v:.3f} V")
    except ValueError:
        pass

ser.close()

# --- Convert to DataFrame and export to Excel ---
df = pd.DataFrame(records)

# Save to Excel (requires openpyxl)
df.to_excel(EXCEL_FILE, index=False, engine="openpyxl")
print(f"Saved {len(df)} samples to {EXCEL_FILE}")

# --- Plot the data ---
plt.figure(figsize=(8, 4))
plt.plot(df["Sample"], df["Voltage (V)"], marker=".")
plt.title("ESP32 Analog Signal (10 Hz)")
plt.xlabel("Sample")
plt.ylabel("Voltage (V)")
plt.grid(True)
plt.tight_layout()
plt.show()
