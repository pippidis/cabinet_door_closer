import RPi.GPIO as GPIO
import time

# === CONFIG ===
PIR_PIN = 11       # Physical pin 11
BUTTON_PIN = 12    # Physical pin 12
RELAY_PIN = 15     # Physical pin 15
LED_PIN = 23       # Physical pin 23
NO_MOTION_TIMEOUT = 600  # 10 minutes in seconds
SOLENOID_ON_TIME = 5     # Seconds to open solenoid

# === SETUP ===
GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIR_PIN, GPIO.IN)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Pull-up resistor

GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.HIGH)  # Low level trigger

GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.LOW)  # LED off by default


last_motion_time = time.time()

def activate_solenoid():
    print("Activating solenoid")
    GPIO.output(RELAY_PIN, GPIO.LOW)
    time.sleep(SOLENOID_ON_TIME)
    GPIO.output(RELAY_PIN, GPIO.HIGH)
    print("Solenoid deactivated")


print("System ready. Monitoring motion and button...")

try:
    waiting_for_motion = False
    last_motion_time = time.time()
    last_debug_print = time.time()
    printed_waiting_message = False

    while True:
        pir_state = GPIO.input(PIR_PIN)
        button_state = GPIO.input(BUTTON_PIN)
        relay_state = GPIO.input(RELAY_PIN)

        # PIR: motion detected
        if pir_state:
            print("Motion detected!")
            GPIO.output(LED_PIN, GPIO.HIGH)  # Turn LED on
            last_motion_time = time.time()
            waiting_for_motion = False
            printed_waiting_message = False
            time.sleep(1)  # debounce
        else:
            GPIO.output(LED_PIN, GPIO.LOW)  # Turn LED off when no motion


        # Manual button
        if button_state == GPIO.LOW:
            print("Manual button pressed")
            activate_solenoid()
            time.sleep(0.5)  # debounce

        # Time since last motion
        time_since_motion = time.time() - last_motion_time

        # If not in waiting state, print countdown every 10 seconds
        if not waiting_for_motion and (time.time() - last_debug_print >= 10):
            remaining = int(NO_MOTION_TIMEOUT - time_since_motion)
            if remaining > 0:
                print("No motion for {} seconds - {}s until solenoid triggers.".format(
                    int(time_since_motion), remaining
                ))
            last_debug_print = time.time()

        # Trigger solenoid after timeout
        if not waiting_for_motion and time_since_motion >= NO_MOTION_TIMEOUT:
            print("No motion for {} seconds - triggering solenoid.".format(NO_MOTION_TIMEOUT))
            activate_solenoid()
            waiting_for_motion = True
            last_motion_time = time.time()
            printed_waiting_message = False 

        # Print once when waiting
        if waiting_for_motion and not printed_waiting_message:
            print("Waiting for motion to reset timer...")
            printed_waiting_message = True

        time.sleep(0.1)

except KeyboardInterrupt:
    print("Exiting...")
finally:
    GPIO.cleanup()
