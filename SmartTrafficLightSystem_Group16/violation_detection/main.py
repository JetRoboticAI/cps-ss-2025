from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from picamera2 import Picamera2
import cv2
import threading
import asyncio
import numpy as np
import base64
import os
import logging
import httpx

import paho.mqtt.client as mqtt
import json
from datetime import datetime, timezone
import time

# Logger configuration
logger = logging.getLogger("video_stream")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

UTILITY_API_URL = "http://104.168.34.100:5555/v1/image/alpr"

# -------- MQTT Settings --------
MQTT_BROKER = 'mqtt-dashboard.com'  # MQTT broker address
INTERSECTION_ID = '0'
MQTT_COMMAND_TOPIC = f'traffic_violation/{INTERSECTION_ID}/detected'

def publish_violation(plate: str, image_bytes: bytes):
    report = (traffic_light["timestamp"], plate)
    if report in reports:
        return
    reports.add(report)
    
    payload = {
        "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat() + "Z",
        "plate": plate,
        "intersection_id": INTERSECTION_ID,
        "image": base64.b64encode(image_bytes).decode('utf-8')
    }
    try:
        mqtt_client.publish(MQTT_COMMAND_TOPIC, json.dumps(payload))
        logger.info(f"Published violation: {payload}"[:150])
    except Exception as e:
        logger.error(f"Failed to publish violation: {str(e)}")


# Asynchronous license plate recognition
async def get_plate(image_bytes: bytes) -> str:
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.post(
                UTILITY_API_URL,
                files={"upload": ("plate.jpg", image_bytes, "image/jpeg")}
            )
        if response.status_code != 200:
            logger.error(f"API error: {response.status_code} - {response.text}")
            return ""
        predictions = response.json().get("predictions", [])
        if not predictions:
            logger.info("No plate detected")
            return ""
        plate = predictions[0].get("plate", "")
        return plate
    except Exception as e:
        logger.error(f"Plate API error: {str(e)}")
        return ""

app = FastAPI()

# Camera initialization
picam2 = Picamera2()
config = picam2.create_video_configuration(
    main={"size": (640, 480)},
    controls={"FrameRate": 30}
)
picam2.configure(config)
picam2.start()

# Thread-safe FrameBuffer
class FrameBuffer:
    def __init__(self):
        self.frame = None
        self.lock = threading.Lock()
    def update(self, frame):
        with self.lock:
            self.frame = frame
    def get_frame(self):
        with self.lock:
            frame = self.frame
        if frame is not None:
            return frame.copy()
        return None
frame_buffer = FrameBuffer()

# Camera frame capture thread
def capture_frames():
    while True:
        frame = picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame_buffer.update(frame)
capture_thread = threading.Thread(target=capture_frames, daemon=True)
capture_thread.start()

# Top-level variable for storing traffic light status
traffic_light = {}

# Traffic light status monitoring thread
def monitor_traffic_light():
    global traffic_light
    while True:
        try:
            with open("/tmp/traffic_light.json", "r") as f:
                data = json.load(f)
                traffic_light = data
        except Exception as e:
            logger.warning(f"Failed to read traffic light file: {str(e)}")
        finally:
            time.sleep(0.01)

# Start traffic light monitoring thread
traffic_light_thread = threading.Thread(target=monitor_traffic_light, daemon=True)
traffic_light_thread.start()

# Already reported violations
reports = set()

# MJPEG stream generator (core improvement)
async def generate_mjpeg():
    frame_count = 0
    recognition_interval = 30  # Recognize every 30 frames (approximately every second)

    recognition_running = False  # Local state

    async def run_recognition(jpeg_bytes):
        nonlocal recognition_running
        try:
            plate = await get_plate(jpeg_bytes)
            if plate:
                logger.info(f"Detected plate: {plate}")
                publish_violation(plate, jpeg_bytes)
        finally:
            recognition_running = False

    while True:
        # Fetch frame in a separate thread to avoid blocking the main event loop
        frame = await asyncio.to_thread(frame_buffer.get_frame)
        if frame is None:
            await asyncio.sleep(0.01)
            continue
        _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        jpeg_bytes = jpeg.tobytes()

        # Run only one recognition async task
        if frame_count % recognition_interval == 0 and not recognition_running and traffic_light and traffic_light['status'] == "Red":
                
            recognition_running = True
            asyncio.create_task(run_recognition(jpeg_bytes))

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + 
               jpeg_bytes + b'\r\n')
        frame_count += 1
        await asyncio.sleep(0.033)  # Wait slightly to maintain 30fps

@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(generate_mjpeg(),
                             media_type='multipart/x-mixed-replace; boundary=frame')

@app.get("/")
async def root():
    return {"message": "Connect to /video_feed for streaming."}

if __name__ == "__main__":
    client = mqtt.Client()
    client.connect(MQTT_BROKER)
    mqtt_client = client
    client.loop_start()

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)