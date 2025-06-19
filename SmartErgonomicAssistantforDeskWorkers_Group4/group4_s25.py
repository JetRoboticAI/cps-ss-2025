# Group 4 S25 - Ergonomic Assistant Script
# This script monitors user posture and distance from the monitor,
# provides reminders for breaks and hydration, and logs events to Google Sheets.

import RPi.GPIO as GPIO
import time
from lcd import drivers  # LCD driver for displaying messages
import gspread  # Google Sheets integration
from oauth2client.service_account import ServiceAccountCredentials  # Auth for Sheets
from datetime import datetime

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


# Pin Setup
POSTURE_TRIG, POSTURE_ECHO = 23, 24
MONITOR_TRIG, MONITOR_ECHO = 27, 22
RGB_RED, RGB_GREEN, RGB_BLUE = 19, 26, 13
BUTTON = 20

# GPIO mode configuration
GPIO.setup(POSTURE_TRIG, GPIO.OUT)
GPIO.setup(POSTURE_ECHO, GPIO.IN)
GPIO.setup(MONITOR_TRIG, GPIO.OUT)
GPIO.setup(MONITOR_ECHO, GPIO.IN)
GPIO.setup(RGB_RED, GPIO.OUT)
GPIO.setup(RGB_GREEN, GPIO.OUT)
GPIO.setup(RGB_BLUE, GPIO.OUT)
GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# Time and Interval Tracking
last_break_time = time.time()
last_water_time = time.time()
data_log_time = time.time()

# User-defined intervals
break_interval_minutes = 1
water_interval_minutes = 2
sheet_update_interval_seconds = 120
check_interval_seconds = 2

# Distance thresholds (in cm)
POSTURE_GOOD_DISTANCE_MIN = 0
POSTURE_GOOD_DISTANCE_MAX = 10
MONITOR_SAFE_DISTANCE_MIN = 50
MONITOR_SAFE_DISTANCE_MAX = 76
MONITOR_DANGEROUS_DISTANCE = 30


# Google Sheets Setup
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
CREDS_FILE = '/home/admin/Desktop/Group_4_S25/credentials.json'

try:
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open('Ergonomic Assistant Data').sheet1
    if not sheet.row_values(1):
        sheet.append_row(["Timestamp", "Event Type", "Details"])
except Exception as e:
    print(f"Error connecting to Google Sheets: {e}")
    sheet = None

event_buffer = []


# Logging Functions
def log_event(event_type, details=""):
    """
    Appends timestamped event data to a buffer for Google Sheets.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    event_buffer.append([timestamp, event_type, details])

def flush_event_buffer():
    """
    Flushes the event buffer to Google Sheets (batch insert).
    """
    global event_buffer
    if sheet and event_buffer:
        try:
            sheet.append_rows(event_buffer)
            event_buffer = []
        except Exception as e:
            print(f"Failed to flush buffer to Google Sheet: {e}")


# LCD Setup and Display
try:
    lcd = drivers.Lcd()
except Exception as e:
    print(f"LCD error: {e}")
    lcd = None

def lcd_display(message, line=1):
    """
    Displays a message on a specific line of the LCD.
    """
    if lcd:
        try:
            lcd.lcd_display_string(message.ljust(16), line)
        except Exception as e:
            print(f"LCD display error: {e}")


# LED Helper
def set_rgb_led(red, green, blue):
    """
    Sets the RGB LED color.
    """
    GPIO.output(RGB_RED, red)
    GPIO.output(RGB_GREEN, green)
    GPIO.output(RGB_BLUE, blue)


# Distance Measurement
def get_distance(TRIG, ECHO):
    """
    Measures distance using an ultrasonic sensor.
    Returns distance in cm or -1 on timeout.
    """
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    pulse_start = time.time()
    pulse_end = time.time()

    # Wait for echo to go high
    timeout_start = time.time()
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
        if time.time() - timeout_start > 0.1:
            return -1

    # Wait for echo to go low
    timeout_start = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
        if time.time() - timeout_start > 0.1:
            return -1

    pulse_duration = pulse_end - pulse_start
    return round(pulse_duration * 17150, 2)


# Monitoring Functions
def check_posture():
    """
    Checks user posture and gives feedback via LED and LCD.
    """
    distance = get_distance(POSTURE_TRIG, POSTURE_ECHO)
    if distance == -1:
        return

    if POSTURE_GOOD_DISTANCE_MIN <= distance <= POSTURE_GOOD_DISTANCE_MAX:
        set_rgb_led(False, True, False)
        lcd_display("Good Posture :)", 1)
        lcd_display(" " * 16, 2)
    else:
        set_rgb_led(True, False, False)
        log_event("Bad Posture", f"Distance: {distance} cm")
        lcd_display("Bad Posture!", 1)
        lcd_display("Adjust now!", 2)

def check_monitor_distance():
    """
    Checks user distance from monitor and gives feedback.
    """
    distance = get_distance(MONITOR_TRIG, MONITOR_ECHO)
    if distance == -1:
        return

    if MONITOR_SAFE_DISTANCE_MIN <= distance <= MONITOR_SAFE_DISTANCE_MAX:
        lcd_display("Good Distance", 1)
        lcd_display("From Monitor :)", 2)
        set_rgb_led(False, True, False)
    elif distance < MONITOR_DANGEROUS_DISTANCE:
        set_rgb_led(True, False, False)
        log_event("Too Close to Monitor", f"Distance: {distance} cm")
        lcd_display("Too Close!", 1)
        lcd_display("Move back!", 2)
    elif distance < MONITOR_SAFE_DISTANCE_MIN:
        set_rgb_led(True, True, False)
        lcd_display("Closer than ideal", 1)
        lcd_display("Consider moving", 2)


# Acknowledgment Button Check
def button_acknowledged():
    """
    Detects button press from the user (with debounce).
    """
    if GPIO.input(BUTTON) == GPIO.LOW:
        time.sleep(0.05)
        if GPIO.input(BUTTON) == GPIO.LOW:
            return True
    return False


# Reminders
def break_reminder():
    """
    Reminds the user to take a break at set intervals.
    Waits up to 30 seconds for acknowledgment.
    """
    global last_break_time
    if (time.time() - last_break_time) > (break_interval_minutes * 60):
        set_rgb_led(False, True, True)
        lcd_display("Take a short", 1)
        lcd_display("walk!", 2)

        start = time.time()
        while time.time() - start < 30:
            if button_acknowledged():
                last_break_time = time.time()
                lcd_display("Break Acknowled-", 1)
                lcd_display("ged! Thank You :)", 2)
                log_event("Break Acknowledged")
                break
            time.sleep(0.1)
        else:
            log_event("Break Not Acknowledged", "User did not respond")
            lcd_display("Break Skipped!", 1)

        set_rgb_led(False, True, False)

def water_reminder():
    """
    Reminds the user to drink water at set intervals.
    Waits up to 30 seconds for acknowledgment.
    """
    global last_water_time
    if (time.time() - last_water_time) > (water_interval_minutes * 60):
        set_rgb_led(True, False, True)
        lcd_display("Time to drink", 1)
        lcd_display("water!", 2)

        start = time.time()
        while time.time() - start < 30:
            if button_acknowledged():
                last_water_time = time.time()
                lcd_display("Water Break", 1)
                lcd_display("Acknowledged! :)", 2)
                log_event("Water Acknowledged")
                break
            time.sleep(0.1)
        else:
            log_event("Water Not Acknowledged", "User did not respond")
            lcd_display("Water Skipped!", 1)

        set_rgb_led(False, True, False)


# Main Loop
try:
    set_rgb_led(False, False, False)
    if lcd:
        lcd.lcd_display_string("Ergonomic Asst.", 1)
        lcd.lcd_display_string("Monitoring...", 2)

    last_posture_check = time.time()
    last_monitor_check = time.time()

    while True:
        now = time.time()

        # Check posture every 2 seconds + 3 sec delay for feedback
        if now - last_posture_check >= check_interval_seconds:
            check_posture()
            time.sleep(3)  # Prevent loop rush and show feedback
            last_posture_check = now

        # Check monitor distance every 2 seconds
        if now - last_monitor_check >= check_interval_seconds:
            check_monitor_distance()
            last_monitor_check = now

        # Run break and water reminders
        break_reminder()
        water_reminder()

        # Flush logs to Google Sheets periodically
        if (now - data_log_time) >= sheet_update_interval_seconds:
            flush_event_buffer()
            data_log_time = now

        time.sleep(1)  # Loop delay to avoid 100% CPU usage


# Cleanup on Exit

except KeyboardInterrupt:
    pass
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    flush_event_buffer()
    set_rgb_led(False, False, False)
    if lcd:
        try:
            lcd.lcd_clear()
            lcd.lcd_display_string("Goodbye!", 1)
        except Exception as e:
            print(f"LCD exit error: {e}")
    GPIO.cleanup()
