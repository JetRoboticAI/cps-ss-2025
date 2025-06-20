import time
import json
import queue
import threading
import paho.mqtt.client as mqtt
from flask import Flask, request

app = Flask(__name__)

@app.route('/receive-order', methods=['POST'])
def receive_order():
    try:
        order = request.get_json()
        if not order:
            return {"error": "Invalid JSON"}, 400

        # Fixed ingredient order
        all_ingredients = ["A", "B", "C", "D"]

        # Dish to ingredient-count mapping
        dish_map = {
            "sandwich": {"A": 2, "B": 1},
            "burger": {"A": 2, "C": 1},
            "chicken": {"A": 1, "B": 2, "C": 1, "D": 1},
            "noodles": {"A": 1, "D": 1},
            "rice": {"B": 2, "D": 1},
            "beef": {"A": 1, "B": 1, "C": 1},
            "vegetable": {"C": 2},
            "egg": {"D": 2}
        }

        # chicken, sandwich, rice, beef, vegetable

        dish = order.get("dish")
        if dish not in dish_map:
            return {"error": "Unknown dish"}, 400
        
        pos = [0] * len(all_ingredients)
        count = [0] * len(all_ingredients)
        print(dish_map[dish])
        for idx, ing in enumerate(all_ingredients):
            if ing in dish_map[dish]:
                pos[idx] = 1
                count[idx] = dish_map[dish][ing]
        cmd = {
            "flag": 0,
            "pos": pos,
            "count": count
        }

        cmdQueue.put(cmd)
        with logLock:
            log_entries.append({"received_order": order, "cmd": cmd})
        return {"status": "Order received", "cmd": cmd}, 200
    except Exception as e:
        return {"error": str(e)}, 500


MQTT_BROKER = "broker.hivemq.com"
CMD_TOPIC = "dispenser/test/esp32/open"
STATUS_TOPIC = "dispenser/status/#"
PING_TOPIC = "dispenser/test/esp32/ping"

errorCount = 0
rebootCount = 0
MAX_ERRORS = 5
MAX_REBOOTS = 3

attReady = threading.Event()
dispenserStatus = ""
cmdQueue = queue.Queue()
logLock = threading.Lock()
log_entries = []

# cmdQueue.put({"flag": 0, "pos": [1, 1, 1, 1], "count": [1, 1, 1, 1]})
# cmdQueue.put({"flag": 0, "pos": [1, 1, 0, 1], "count": [1, 2, 0, 1]})
# cmdQueue.put({"flag": 0, "pos": [0, 1, 0, 0], "count": [0, 1, 0, 0]})


# cmdQueue.put({"flag": 0, "pos": [1, 1, 1, 1], "count": [1, 1, 1, 1]})
# cmdQueue.put({"flagcount": [1, 1, 1, 1]})
# cmdQueue.put({"flag": 99, "pos": [5, 2, 1, 1], "count": [2, 1, 1, 2]})
# cmdQueue.put({"flag": 0, "pos": [1, 0, 1, 1], "count": [-1, 0, -2, 1]})
# cmdQueue.put({"flag": -1, "pos": [0, 1, 0, 0], "count": [0, 1, 0, 0]})
# cmdQueue.put("this is not a CMD")
# cmdQueue.put({"CMD": "reboot", "count": rebootCount})


def onConnect(client, userdata, flags, rc):
    print("Connected to broker")
    client.subscribe(STATUS_TOPIC)
    client.publish(PING_TOPIC, json.dumps({"CMD":"ping"}))

def onMessage(client, userdata, msg):
    global dispenserStatus, errorCount
    try:
        payload = json.loads(msg.payload.decode())
        print(payload)
        if "att" in payload:
            newStatus = payload["status"]
            if payload["att"] == False:
                print(newStatus)
                dispenserStatus = newStatus
                attReady.set()
                # Log status update
                with logLock:
                    log_entries.append({"status": newStatus})
            elif payload["att"] == True:
                print("Pausing CMD")
                dispenserStatus = newStatus
                attReady.clear()
                with logLock:
                    log_entries.append({"status": newStatus})
                if newStatus.startswith("ERROR"):
                    errorCount += 1
                    print(f"Error count: {errorCount}")
                else:
                    errorCount = 0
        else:
            print("Received message:", payload)
    except json.JSONDecodeError:
        print("Error decoding JSON payload:", msg.payload.decode())

def sendCommand(client):
    cmd = cmdQueue.get()
    print("Sending CMD:", cmd)
    client.publish(CMD_TOPIC, json.dumps(cmd))
    attReady.clear()
    # Log sent command
    with logLock:
        log_entries.append({"cmd": cmd})
    print("Waiting for CMD to complete")

def write_log(entries):
    with open("log.txt", "a") as f:
        f.write(f"\n--- Execution at {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        for entry in entries:
            if "cmd" in entry:
                f.write(f"Command Sent: {json.dumps(entry['cmd'])}\n")
            elif "status" in entry:
                f.write(f"Status Reported: {entry['status']}\n")
        f.write(f"--- End of Execution ---\n")

def main():
    global errorCount, rebootCount, dispenserStatus
    client = mqtt.Client()
    client.on_connect = onConnect
    client.on_message = onMessage

    client.connect(MQTT_BROKER, 1883, 60)
    client.loop_start()

    try:
        while not attReady.is_set():
            time.sleep(0.2)
        while True:
            if rebootCount >= MAX_REBOOTS:
                print("Max reboots reached, exiting")
                break
            if errorCount >= MAX_ERRORS:
                print("Rebooting")
                client.publish(PING_TOPIC, json.dumps({"CMD": "reboot", "count": rebootCount}))
                dispenserStatus = "REBOOTING"
                attReady.clear()
                errorCount = 0
                rebootCount += 1
            if not cmdQueue.empty():
                if attReady.is_set():
                    sendCommand(client)
                else:
                    print("Waiting " + dispenserStatus)
            else:
                print("No cmd")
                time.sleep(1)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Exit")
    finally:
        client.loop_stop()
        client.disconnect()
        write_log(log_entries)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=8000, debug=False, use_reloader=False))
    flask_thread.daemon = True
    flask_thread.start()
    main()

