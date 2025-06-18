import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO
import json
import ssl
from paho.mqtt import client as mqtt_client
from database import SessionLocal, Patient
from collections import deque

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

patient_queue = deque()
average_handling_time = 3  # minutes
manual_patient_counter = 20

# MQTT Config
MQTT_BROKER = 'broker.emqx.io'
MQTT_PORT = 8883
MQTT_TOPIC = '/ranaharshil/cloud'
MQTT_USERNAME = 'emqx'
MQTT_PASSWORD = 'public'
CA_CERT = './ca_certificate.pem'

def send_msg_to_mqtt(client, topic, payload):
    try:
        client.publish(topic, payload)
    except Exception as e:
        print("MQTT publish error:", e)

@socketio.on("send_mqtt")
def handle_send_mqtt(data):
    global manual_patient_counter
    manual_patient_counter += 1
    patient_id = manual_patient_counter

    message = {
        "newPatient": 1,
        "patientID": patient_id
    }

    print(f"📤 Sending manual MQTT message for Patient #{patient_id}")
    send_msg_to_mqtt(mqtt_client, MQTT_TOPIC, json.dumps(message))
    socketio.emit("token_issued", {"patientID": patient_id})


def determine_health_status(bpm, spo2, temp):
    if bpm < 60 or bpm > 100 or spo2 < 90:
        return "Poor"
    elif bpm < 80 or spo2 < 95 or temp < 36.5 or temp > 37:
        return "Average"
    else:
        return "Excellent"

def update_queue(patient_id):
    if patient_id not in patient_queue:
        patient_queue.append(patient_id)
    position = list(patient_queue).index(patient_id)
    return position, position * average_handling_time

def on_connect(client, userdata, flags, rc):
    print("✅ Connected to MQTT with code:", rc)
    client.subscribe(MQTT_TOPIC)
    print("📡 Subscribed to topic:", MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        print("📥 MQTT received:", payload)
        data = json.loads(payload)

        patient_id = data.get("patientID")
        bpm = data.get("currentBPM")
        spo2 = data.get("currentSpO2")
        temp = data.get("currentTemp")

        if patient_id is None or bpm is None or spo2 is None or temp is None:
            print("⚠️ Incomplete data, skipping...")
            return

        health_status = determine_health_status(bpm, spo2, temp)

        # Ensure patient is in queue
        if patient_id not in patient_queue:
            patient_queue.append(patient_id)

        # Use incoming waiting time to derive queue position
        incoming_waiting_time = data.get("waitingTime")
        if incoming_waiting_time is not None:
            waiting_time = incoming_waiting_time
            position = waiting_time // average_handling_time
        else:
            position = list(patient_queue).index(patient_id)
            waiting_time = position * average_handling_time

        enriched_data = {
            "patientID": patient_id,
            "currentBPM": bpm,
            "currentSpO2": spo2,
            "currentTemp": temp,
            "emergencyState": data.get("emergencyState", False),
            "healthStatus": health_status,
            "queuePosition": position + 1,
            "waitingTime": waiting_time
        }

        socketio.emit("mqtt_data", enriched_data)

        # Save to DB
        db = SessionLocal()
        patient = Patient(
            patientID=patient_id,
            bpm=bpm,
            spo2=spo2,
            temp=temp,
            healthStatus=health_status,
            waitingTime=waiting_time,
        )
        db.add(patient)
        db.commit()
        db.close()
        print(f"💾 Stored patient {patient_id} in DB")

        # Send response to MQTT
        response_payload = {
            "patientID": patient_id,
            "healthStatus": health_status,
            "waitingTime": waiting_time
        }
        send_msg_to_mqtt(client, MQTT_TOPIC, json.dumps(response_payload))
        print(f"🔁 Sent response to MQTT: {response_payload}")

    except Exception as e:
        print("❌ Error handling MQTT message:", e)
    
        print("❌ Error handling MQTT message:", e)

# MQTT Client Setup
mqtt_client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1)
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
mqtt_client.tls_set(ca_certs=CA_CERT, tls_version=ssl.PROTOCOL_TLS)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
mqtt_client.loop_start()

# Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/request_token")
def request_token():
    return render_template("request.html")

# Start Server
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5050)
