import RPi.GPIO as GPIO
import time

# --- Setup ---
BUTTON_PIN = 26  # GPIO26 (physical pin 37)
GPIO.setmode(GPIO.BCM)  # use BCM numbering
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # enable internal pull-down too

print("Ready! Press the button on GPIO26 (pin 37). Press Ctrl+C to exit.")

try:
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.HIGH:
            print("Button pressed!")
            time.sleep(0.2)  # debounce delay
        else:
            time.sleep(0.05)

except KeyboardInterrupt:
    print("\nExiting program...")

finally:
    GPIO.cleanup()
