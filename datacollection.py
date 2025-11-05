#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk
import time, json, threading, statistics, signal, sys, os
from datetime import datetime

# ---------------- CONFIG ----------------
VREF = 3.3
ADC_CHANNEL = 0
SAMPLE_HZ = 600
REST_SECONDS = 3.0
CONTRACT_SECONDS = 3.0

BASELINE_MODE = "ema"  # "static" or "ema"
EMA_ALPHA = 0.02
EMA_GUARD_PCT = 15.0
# ----------------------------------------

# -------- MCP3204 SPI Interface ---------
class MCP3204:
    def __init__(self, bus=0, device=0, vref=3.3):
        import spidev
        self.vref = float(vref)
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = 1350000
        self.spi.mode = 0

    def read_raw(self, ch=0):
        cmd = [0x06, (ch & 0x07) << 6, 0x00]
        b0, b1, b2 = self.spi.xfer2(cmd)
        return ((b1 & 0x0F) << 8) | b2

    def read_voltage(self, ch=0):
        return (self.read_raw(ch) / 4095.0) * self.vref

    def close(self):
        try:
            self.spi.close()
        except:
            pass

# -------- Sampling Helper --------------
def sample_average_voltage(adc, ch, duration_s, sample_hz):
    interval = 1.0 / float(sample_hz)
    samples = []
    t0 = time.time()
    while (time.time() - t0) < duration_s:
        samples.append(adc.read_voltage(ch))
        time.sleep(interval)
    avg = statistics.mean(samples) if samples else 0.0
    return avg, samples

# -------------- GUI APP ----------------
class EMGApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EMG Calibration & Live Monitor")
        self.root.geometry("700x400")
        self.root.configure(bg="black")

        self.adc = MCP3204(bus=0, device=0, vref=VREF)
        self.v_min = self.v_max = self.baseline = 0.0
        self.running = False
        self.stop_thread = False

        # UI Elements
        self.status_label = tk.Label(root, text="WELCOME", fg="lime", bg="black", font=("Courier", 20))
        self.status_label.pack(pady=20)

        self.result_label = tk.Label(root, text="", fg="white", bg="black", font=("Helvetica", 12))
        self.result_label.pack(pady=5)

        self.start_rest_btn = ttk.Button(root, text="Calibrate REST", command=self.calibrate_rest)
        self.start_rest_btn.pack(pady=5)

        self.start_contract_btn = ttk.Button(root, text="Calibrate CONTRACTED", command=self.calibrate_contract)
        self.start_contract_btn.pack(pady=5)

        self.start_live_btn = ttk.Button(root, text="Start Live Monitor", command=self.start_live)
        self.start_live_btn.pack(pady=5)

        self.live_label = tk.Label(root, text="", fg="cyan", bg="black", font=("Consolas", 16))
        self.live_label.pack(pady=10)

        self.progress = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate", maximum=100)
        self.progress.pack(pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def set_status(self, msg, color="white"):
        self.status_label.config(text=msg, fg=color)
        self.root.update()

    def calibrate_rest(self):
        self.set_status("CALIBRATING REST...", "yellow")
        avg, _ = sample_average_voltage(self.adc, ADC_CHANNEL, REST_SECONDS, SAMPLE_HZ)
        self.rest_avg = avg
        self.result_label.config(text=f"Rest avg: {avg:.4f} V")
        self.set_status("REST DONE", "lime")

    def calibrate_contract(self):
        self.set_status("CALIBRATING CONTRACTED...", "yellow")
        avg, _ = sample_average_voltage(self.adc, ADC_CHANNEL, CONTRACT_SECONDS, SAMPLE_HZ)
        self.contract_avg = avg
        self.v_min = min(self.rest_avg, self.contract_avg)
        self.v_max = max(self.rest_avg, self.contract_avg)
        self.baseline = self.rest_avg
        self.result_label.config(
            text=f"Contracted avg: {avg:.4f} V | Range: {self.v_min:.3f}-{self.v_max:.3f}V"
        )
        self.set_status("CONTRACTED DONE", "lime")

        cal = {
            "timestamp": datetime.now().isoformat(),
            "adc": "MCP3204",
            "vref": VREF,
            "adc_channel": ADC_CHANNEL,
            "rest_avg_v": self.rest_avg,
            "contracted_avg_v": self.contract_avg,
            "v_min": self.v_min,
            "v_max": self.v_max,
        }
        with open("emg_calibration.json", "w") as f:
            json.dump(cal, f, indent=2)

    def start_live(self):
        if not hasattr(self, "v_min") or self.v_max == self.v_min:
            self.set_status("Calibrate first!", "red")
            return
        self.set_status("LIVE MONITOR", "cyan")
        self.running = True
        self.stop_thread = False
        threading.Thread(target=self.live_loop, daemon=True).start()

    def live_loop(self):
        while not self.stop_thread:
            v = self.adc.read_voltage(ADC_CHANNEL)
            # Bias correction
            if BASELINE_MODE == "ema":
                denom = max(1e-9, (self.v_max - self.baseline))
                pct_now = max(0, min(100, ((v - self.baseline) / denom) * 100))
                if pct_now < EMA_GUARD_PCT:
                    self.baseline = (1 - EMA_ALPHA) * self.baseline + EMA_ALPHA * v
            else:
                self.baseline = self.rest_avg

            pct = max(0, min(100, ((v - self.baseline) / (self.v_max - self.baseline)) * 100))
            self.progress["value"] = pct
            self.live_label.config(text=f"Voltage={v:.4f}V  Baseline={self.baseline:.4f}V  {pct:6.2f}%")
            self.root.update()
            time.sleep(1 / SAMPLE_HZ)

    def on_close(self):
        self.stop_thread = True
        self.adc.close()
        self.root.destroy()

def main():
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    root = tk.Tk()
    app = EMGApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
    