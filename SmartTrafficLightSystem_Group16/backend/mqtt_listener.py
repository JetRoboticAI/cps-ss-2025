#cd traffic_light_backend
#python flask_server.py
import json
import sqlite3
import paho.mqtt.client as mqtt
import sys
import time
from datetime import datetime
import os

MQTT_BROKER = 'mqtt-dashboard.com'
MQTT_PORT = 1883

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'traffic_data.db')

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            type TEXT,
            plate TEXT,
            location TEXT,
            image_base64 TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS light_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            status TEXT,
            intersection_id TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_violation(raw_data):
    try:
        data = {
            "timestamp": raw_data.get("timestamp"),
            "type": raw_data.get("violation_type"),
            "plate": raw_data.get("plate"),
            "location": raw_data.get("intersection_id"),
            "image": raw_data.get("image")
        }

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO violations (timestamp, type, plate, location, image_base64)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data["timestamp"],
            data["type"],
            data["plate"],
            data["location"],
            data["image"]
        ))
        conn.commit()
        conn.close()
        print("[DB] Record inserted:", data)
    except Exception as e:
        print("[ERROR] Failed to insert:", e)

def insert_light_status(data):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO light_status (timestamp, status, intersection_id)
            VALUES (?, ?, ?)
        ''', (
            data.get('timestamp'),
            data.get('status'),
            data.get('intersection_id')
        ))
        conn.commit()
        conn.close()
        print("[DB] Light status inserted:", data)
    except Exception as e:
        print("[ERROR] Failed to insert light status:", e)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[MQTT] ✅ Connected successfully.")
        client.subscribe("traffic_violation/+/detected")
        client.subscribe("traffic_light/+/status")
        print("[MQTT] Subscribed to topics: traffic_violation/+/detected, traffic_light/+/status")
    else:
        print(f"[MQTT] ❌ Failed to connect, return code: {rc}")

def on_message(client, userdata, msg):
    print(f"[MQTT] Message received on topic: {msg.topic}")
    try:
        data = json.loads(msg.payload.decode())
        print(f"[MQTT] Payload: {data}")

        if msg.topic.startswith("traffic_violation/"):
            insert_violation(data)
        elif msg.topic.startswith("traffic_light/") and msg.topic.endswith("/status"):
            insert_light_status(data)
        else:
            print("[MQTT] Unknown topic:", msg.topic)

    except Exception as e:
        print("[ERROR] MQTT message processing failed:", e)

def start_mqtt():
    init_db()
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

def run_test_inserts(n=5):
    init_db()
    for i in range(n):
        test_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "Running Red",
            "plate": f"TEST{i:03}",
            "location": "Intersection X",
            "image": None
        }
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO violations (timestamp, type, plate, location, image_base64)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            test_data["timestamp"],
            test_data["type"],
            test_data["plate"],
            test_data["location"],
            test_data["image"]
        ))
        conn.commit()
        conn.close()
        print("[DB] Test data inserted:", test_data)
        time.sleep(1)

if __name__ == '__main__':
    print("[MODE] MQTT listener starting...")
    start_mqtt()
