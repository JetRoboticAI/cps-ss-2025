import serial
import time
import BlynkLib
from datetime import datetime
import sys

# Ensure stdout uses UTF-8 encoding for proper character display
sys.stdout.reconfigure(encoding='utf-8')

# Blynk authentication token and initialization
BLYNK_AUTH = 'zrqCeEyajW-9EKj_Ymql0ZOP4ALcsV2u'
blynk = BlynkLib.Blynk(BLYNK_AUTH)

# Open serial connection to Arduino (adjust port as needed)
arduino = serial.Serial('/dev/ttyACM0', 9600)

last_status = None           # Tracks last door status to avoid duplicate logs
alarm_triggered = False      # Tracks if alarm has been triggered

print("Running servo control bridge...")

# === Data Logging Function to USB ===
def log_to_file(message):
    try:
        with open("/media/capstone/LEXAR/Project_Logs/door_log.txt", "a") as log_file:
            log_file.write(message + "\n")
    except Exception as e:
        print(f"Error writing to log file: {e}")

# === Initial Door Status ===
initial_door_status = "0"    # Simulated initial status; '0' means closed
status = "Door Closed" if initial_door_status == '0' else "Door Opened"
timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
print(f"[Door Status] {status}")
blynk.virtual_write(3, status)      # Update Blynk app
log_to_file(f"[{timestamp}] {status}")

# === Initial Lock Status ===
initial_lock_status = "0"    # Simulated initial lock; '0' means locked
status = "Door Locked" if initial_lock_status == '0' else "Door Unlocked"
timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
print(f"[Lock Status] {status}")
blynk.virtual_write(1, status)      # Update Blynk app
log_to_file(f"[{timestamp}] {status}")

# === Blynk Handlers ===

@blynk.on("V0")
def v0_write_handler(value):
    command = value[0]
    print(f"[Blynk] V0 command: {command}")
    arduino.write(command.encode())

    status = "Door Locked" if command == '0' else "Door Unlocked"
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"[Lock Status] {status}")
    blynk.virtual_write(1, status)
    log_to_file(f"[{timestamp}] {status}")

@blynk.on("V4")
def v4_push_handler(value):
    print("Push Button Trigger")
    arduino.write(b'6')

@blynk.on("V2")
def v2_silence_buzzer(value):
    if value[0] == '1':
        status = "Alarm: Silenced"
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"[Blynk] {status}")
        blynk.virtual_write(5, status)
        arduino.write(b'7')
        log_to_file(f"[{timestamp}] {status}")

# === Main Loop ===
while True:
    blynk.run()  # Process Blynk events

    # Check for incoming data from Arduino
    if arduino.in_waiting > 0:
        try:
            # Read and decode a line from Arduino
            line = arduino.readline().decode('utf-8', errors='ignore').strip()

            # Handle door status changes
            if "Door Opened" in line or "Door Closed" in line:
                if line != last_status:
                    last_status = line
                    status = line
                    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                    print(f"[Door Status] {status}")
                    blynk.virtual_write(3, status)
                    log_to_file(f"[{timestamp}] {status}")

            # Handle alarm trigger from Arduino
            if "ALARM_TRIGGERED" in line and not alarm_triggered:
                alarm_triggered = True
                status = "Alarm: Door left opened"
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                print(f"[ALERT] {status}")
                blynk.virtual_write(5, status)
                log_to_file(f"[{timestamp}] {status}")

            # Reset alarm if door is closed
            if "Door Closed" in line:
                alarm_triggered = False

        except Exception as e:
            print(f"Serial read error: {e}")
