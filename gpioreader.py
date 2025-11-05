#!/usr/bin/env python3
import pigpio, time

PIN = 17
SAMPLE_HZ = 2000           # 2 kHz; adjust as needed
PERIOD = 1.0 / SAMPLE_HZ

pi = pigpio.pi()
if not pi.connected:
    raise SystemExit("pigpio daemon not running")

pi.set_mode(PIN, pigpio.INPUT)
pi.set_pull_up_down(PIN, pigpio.PUD_DOWN)

print(f"Sampling GPIO {PIN} at {SAMPLE_HZ} Hz… Ctrl+C to stop.")
try:
    next_t = time.perf_counter()
    while True:
        level = pi.read(PIN)      # 0 or 1
        ts = time.time()          # seconds since epoch
        print(f"{ts:.6f},{level}")  # CSV line
        next_t += PERIOD
        delay = next_t - time.perf_counter()
        if delay > 0:
            time.sleep(delay)
        else:
            # If we're falling behind, realign
            next_t = time.perf_counter()
except KeyboardInterrupt:
    pass
finally:
    pi.stop()
