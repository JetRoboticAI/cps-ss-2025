import time
import threading
from flask import Flask, request
import RPi.GPIO as GPIO
from huskylib import HuskyLensLibrary

#Motor Driver GPIO Pins
IN1 = 17
IN2 = 27
IN3 = 22
IN4 = 23

#HuskyLens Object IDs
GREEN_ID = 1
RED_ID = 2


mode = "auto" 

#Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup([IN1, IN2, IN3, IN4], GPIO.OUT)

#Motor Control Functions
def stop_motors():
    print("🛑 Stopping motors")
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)

def move_forward():
    print("🚗 Moving forward")
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

#Flask Web Server (for MIT App)
app = Flask(__name__)

@app.route('/motor', methods=['GET'])
def motor_control():
    global mode
    cmd = request.args.get('cmd')
    if cmd == "start":
        mode = "manual"
        move_forward()
        return "Motors started (manual mode)"
    elif cmd == "stop":
        mode = "manual"
        stop_motors()
        return "Motors stopped (manual mode)"
    elif cmd == "auto":
        mode = "auto"
        return "Switched to auto mode (HuskyLens)"
    else:
        return "Invalid command"

def run_flask():
    print("🌐 Starting Flask server on port 5000...")
    app.run(host="0.0.0.0", port=5000)

# HuskyLens Logic
def run_huskylens_loop():
    global mode
    print("🔍 Initializing HuskyLens...")
    huskylens = HuskyLensLibrary("SERIAL", "/dev/serial0", 9600)

    if not huskylens.knock():
        print("❌ HuskyLens connection failed!")
        return
    print("✅ HuskyLens connected.")

    while True:
        if mode == "auto":
            results = huskylens.requestAll()
            if results:
                detected_ids = [obj.ID for obj in results]
                print(f"🎯 Detected IDs: {detected_ids}")
                if RED_ID in detected_ids:
                    stop_motors()
                elif GREEN_ID in detected_ids:
                    move_forward()
                else:
                    stop_motors()
            else:
                print("👀 No objects detected.")
                stop_motors()
        time.sleep(0.5)

if __name__ == "__main__":
    try:
        stop_motors()
        
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()

        # Start HuskyLens loop
        run_huskylens_loop()

    except KeyboardInterrupt:
        print("\n🛑 Program interrupted by user.")
    finally:
        print("🧹 Cleaning up GPIO...")
        GPIO.cleanup()
