"""
Smart Safety Helmet Monitoring System - Group 5 
Version: 1.3.0
Author: Suraj, Vipin, Chris, Purva
Last Updated: 2025-06-17

Description:
This script runs on a Raspberry Pi and monitors a smart safety helmet using:
- MPU6050 (Accelerometer + Gyroscope) for fall detection
- DHT11 for temperature and humidity
- MQ2 Gas sensor
- GPS for location
- Buzzer, RGB LED, and vibration motor for alerts
- Publishes data to Ubidots using MQTT over TLS
"""

# === IMPORTS ===
import smbus
from time import sleep, time
import joblib
import numpy as np
import json
import warnings
import Adafruit_DHT
import RPi.GPIO as GPIO
import serial
import adafruit_gps
import paho.mqtt.client as mqtt
import ssl

warnings.filterwarnings("ignore")

# === UBIDOTS MQTT CONFIGURATION ===
TOKEN = "BBUS-1tLbgTlamRq9DFdEPCnTeUYDCq2NZB"  # Replace with your Ubidots token
DEVICE_LABEL = "smart-safety-helmet"
MQTT_HOST = "industrial.api.ubidots.com"
MQTT_PORT = 8883
MQTT_TOPIC = f"/v1.6/devices/{DEVICE_LABEL}"

client = mqtt.Client()
client.username_pw_set(TOKEN, password="")
client.tls_set_context(ssl.create_default_context())
client.connect(MQTT_HOST, MQTT_PORT)
client.loop_start()

def mqtt_publish(payload):
    """Publishes payload to MQTT topic on Ubidots."""
    try:
        client.publish(MQTT_TOPIC, json.dumps(payload))
        print(f"[MQTT] Data sent: {json.dumps(payload)}")
    except Exception as e:
        print(f"[MQTT ERROR] {e}")

# === MPU6050 SENSOR CONFIGURATION ===
# MPU6050 Registers
PWR_MGMT_1 = 0x6B
SMPLRT_DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
INT_ENABLE = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47

bus = smbus.SMBus(1)
Device_Address = 0x68

def MPU_Init():
    """Initializes MPU6050."""
    bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)
    bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
    bus.write_byte_data(Device_Address, CONFIG, 0)
    bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
    bus.write_byte_data(Device_Address, INT_ENABLE, 1)

def read_raw_data(addr):
    """Reads raw 16-bit value from MPU6050 register."""
    high = bus.read_byte_data(Device_Address, addr)
    low = bus.read_byte_data(Device_Address, addr + 1)
    value = (high << 8) | low
    if value > 32768:
        value -= 65536
    return value

MPU_Init()

# Load ML model for fall detection
model = joblib.load("/home/pi/Desktop/Code Files/fall_detection_rf_model.pkl")

# State variables
fall_count = 0
detection_variable = 0

# === DHT11 CONFIGURATION ===
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4
dht_last_time = 0

# === MQ2 GAS SENSOR CONFIGURATION ===
MQ2_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(MQ2_PIN, GPIO.IN)
mq_last_time = 0

# === BUZZER, RGB LED, VIBRATION MOTOR ===
BUZZER_PIN = 5
LED_RED, LED_GREEN, LED_BLUE = 6, 13, 19
VIBRATION_PIN = 26

GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup([LED_RED, LED_GREEN, LED_BLUE, VIBRATION_PIN], GPIO.OUT)

def set_led_color(red=False, green=False, blue=False):
    """Sets RGB LED color based on parameters."""
    GPIO.output(LED_RED, GPIO.LOW if red else GPIO.HIGH)
    GPIO.output(LED_GREEN, GPIO.LOW if green else GPIO.HIGH)
    GPIO.output(LED_BLUE, GPIO.LOW if blue else GPIO.HIGH)

# === GPS CONFIGURATION ===
uart = serial.Serial("/dev/serial0", baudrate=9600, timeout=10)
gps = adafruit_gps.GPS(uart, debug=False)
gps.send_command(b'PMTK220,1000')  # 1 Hz update rate
gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
gps_last_time = 0

print("[INFO] Starting Smart Safety Helmet Monitoring with MQTT...")

# === MAIN LOOP ===
try:
    while True:
        current_time = time()
        gps.update()

        # === FALL DETECTION ===
        acc_x = read_raw_data(ACCEL_XOUT_H)
        acc_y = read_raw_data(ACCEL_YOUT_H)
        acc_z = read_raw_data(ACCEL_ZOUT_H)
        gyro_x = read_raw_data(GYRO_XOUT_H)
        gyro_y = read_raw_data(GYRO_YOUT_H)
        gyro_z = read_raw_data(GYRO_ZOUT_H)

        # Normalize readings
        Ax, Ay, Az = acc_x / 16384.0, acc_y / 16384.0, acc_z / 16384.0
        Gx, Gy, Gz = gyro_x / 131.0, gyro_y / 131.0, gyro_z / 131.0

        # Run model prediction only when Az is below threshold
        if Az <= 0.50:
            input_data = np.array([[Gx, Gy, Gz, Ax, Ay, Az]])
            prediction = model.predict(input_data)

            if prediction[0] == 1:
                fall_count += 1
                if fall_count >= 4:
                    detection_variable = 1
                    print("[FALL] Detected")
                    GPIO.output(BUZZER_PIN, GPIO.HIGH)
                else:
                    print("[FALL] Possible")
            else:
                fall_count = 0
                detection_variable = 0
                GPIO.output(BUZZER_PIN, GPIO.LOW)
        else:
            fall_count = 0
            detection_variable = 0
            GPIO.output(BUZZER_PIN, GPIO.LOW)

        # Publish MPU6050 data
        mpu_payload = {
            "Detection_Variable": detection_variable,
            "Accel_X": round(Ax, 2),
            "Accel_Y": round(Ay, 2),
            "Accel_Z": round(Az, 2)
        }
        mqtt_publish(mpu_payload)

        # === DHT11 READINGS EVERY 5 SECONDS ===
        if current_time - dht_last_time >= 5:
            humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
            if humidity is not None and temperature is not None:
                dht_payload = {
                    "Temperature": round(temperature, 2),
                    "Humidity": round(humidity, 2)
                }
                mqtt_publish(dht_payload)
            dht_last_time = current_time

        # === MQ2 GAS SENSOR READINGS EVERY 5 SECONDS ===
        if current_time - mq_last_time >= 5:
            gas_status = GPIO.input(MQ2_PIN)
            gas_value = 1 if gas_status == GPIO.LOW else 0
            GPIO.output(VIBRATION_PIN, GPIO.HIGH if gas_value else GPIO.LOW)
            print("[Gas Detected]" if gas_value else "[Clear]")
            mqtt_publish({"GasSensor": gas_value})
            mq_last_time = current_time

        # === GPS DATA EVERY 5 SECONDS ===
        if current_time - gps_last_time >= 5:
            if gps.has_fix and gps.latitude and gps.longitude:
                gps_payload = {
                    "gps": {
                        "value": 1,
                        "context": {
                            "lat": round(gps.latitude, 6),
                            "lng": round(gps.longitude, 6)
                        }
                    }
                }
                mqtt_publish(gps_payload)
            else:
                print("[GPS] No fix yet...")
            gps_last_time = current_time

        # === LED STATUS ===
        if detection_variable == 1:
            set_led_color(red=True)
        elif gas_value == 1:
            set_led_color(blue=True)
        else:
            set_led_color(green=True)

        sleep(1)

# === CLEANUP ON EXIT ===
except KeyboardInterrupt:
    print("\n[INFO] Program terminated by user.")
finally:
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    set_led_color(False, False, False)
    GPIO.cleanup()
    uart.close()
    client.loop_stop()
    client.disconnect()
