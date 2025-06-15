from gpiozero import LED
import time
from queue import Queue
import os

import paho.mqtt.client as mqtt
import json
from datetime import datetime, timezone

# Global settings
STATES = ["Green", "Yellow", "Red"]
STATE_DURATION = 5  # The duration for each state in seconds.

# -------- GPIO：BCM --------
RED_PIN = 17      # Pin 11
YELLOW_PIN = 27   # Pin 13
GREEN_PIN = 22    # Pin 15

red_led = LED(RED_PIN)
yellow_led = LED(YELLOW_PIN)
green_led = LED(GREEN_PIN)

# Local file settings.
TMP_FILE = '/tmp/traffic_light.json'
TMP_TMP_FILE = '/tmp/traffic_light.json.tmp'

# -------- MQTT Settings --------
MQTT_BROKER = 'mqtt-dashboard.com'  # The MQTT broker address.
INTERSECTION_ID = '0'
MQTT_COMMAND_TOPIC = f'traffic_light/{INTERSECTION_ID}/command'
MQTT_STATUS_TOPIC = f'traffic_light/{INTERSECTION_ID}/status'

# -------- Global variables --------
mode = "Auto"            # Current mode: "Auto" or "Manual"
auto_index = 0           # Current light index for auto mode.
current_state = STATES[0]
state_start_time = time.time()
command_queue = Queue()
mqtt_client = None

def publish_status(state):
    """Publish the current state to MQTT and local file."""
    payload = {
        "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat() + "Z",
        "status": state,
        "intersection_id": INTERSECTION_ID
    }

    # Publish to local file.
    with open(TMP_TMP_FILE, 'w') as f:
        f.write(json.dumps(payload))
        f.flush()
        os.fsync(f.fileno())
    os.rename(TMP_TMP_FILE, TMP_FILE)  # rename to ensure atomic write

    # Publish to MQTT.
    try:
        mqtt_client.publish(MQTT_STATUS_TOPIC, json.dumps(payload), qos=1)
    except Exception as e:
        print(f"MQTT publish failed: {e}")

def set_lights(state):
    """Set the lights based on the current state."""
    if state == "Red":
        red_led.on()
        yellow_led.off()
        green_led.off()
    elif state == "Yellow":
        red_led.off()
        yellow_led.on()
        green_led.off()
    elif state == "Green":
        red_led.off()
        yellow_led.off()
        green_led.on()
    else:
        # Turn off all lights if the state is unknown.
        red_led.off()
        yellow_led.off()
        green_led.off()

def set_state(new_state, report=True):
    global current_state, state_start_time
    if new_state != current_state:
        current_state = new_state
        state_start_time = time.time()
        set_lights(new_state)
        if report:
            publish_status(new_state)

def on_message(client, userdata, msg):
    """Handle incoming MQTT messages for the command."""
    payload = msg.payload.decode('utf-8').strip()
    command_queue.put(payload)

def parse_command(command):
    """Parse the incoming command from MQTT."""
    json_command = json.loads(command)
    if isinstance(json_command, dict):
        return json_command.get('command', 'None').strip()
    return command.strip()


def main():
    global mqtt_client, mode, auto_index

    # Initialize GPIO LEDs.
    set_state(STATES[auto_index])

    # Initialize MQTT client.
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(MQTT_BROKER)
    client.subscribe(MQTT_COMMAND_TOPIC)
    mqtt_client = client
    client.loop_start()

    try:
        while True:
            # 1. The manual command queue processing.
            while not command_queue.empty():
                cmd = parse_command(command_queue.get())
                print('Get a command:', cmd)
                if cmd == "Auto":
                    mode = "Auto"
                    # When switching to auto mode, reset the index.
                    auto_index = (auto_index + 1) % len(STATES)
                    set_state(STATES[auto_index])
                elif cmd in STATES:
                    mode = "Manual"
                    set_state(cmd)
                else:
                    print(f"Unknown command: {cmd}")

            # 2. The auto mode state transition.
            now = time.time()
            if mode == "Auto":
                if now - state_start_time >= STATE_DURATION:
                    auto_index = (auto_index + 1) % len(STATES)
                    set_state(STATES[auto_index])

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("Ctrl+C to quit ...")
    finally:
        red_led.off()
        yellow_led.off()
        green_led.off()
        red_led.close()
        yellow_led.close()
        green_led.close()
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()