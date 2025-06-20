import time
import bme680
import paho.mqtt.client as mqtt
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import RPi.GPIO as GPIO
GPIO.setwarnings(False)

# Email Setup
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = '' #Enter sender's email
SENDER_PASSWORD = '' #Enter sender's access token 
RECEIVER_EMAIL = '' #Enter recipient's email

# Sensor and LED Setup
MOTION_SENSOR_PIN = 17 
LED_PIN = 27  

# Button GPIO pins 
INCREASE_BUTTON_PIN = 18  
DECREASE_BUTTON_PIN = 23  

GPIO.setmode(GPIO.BCM)
GPIO.setup(MOTION_SENSOR_PIN, GPIO.IN)  # Motion sensor as input
GPIO.setup(LED_PIN, GPIO.OUT)  # LED as output
GPIO.setup(INCREASE_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  
GPIO.setup(DECREASE_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  

# Initialize BME680 sensor
sensor = bme680.BME680(i2c_addr=0x77)
sensor.set_humidity_oversample(bme680.OS_2X)
sensor.set_temperature_oversample(bme680.OS_8X)
sensor.set_filter(bme680.FILTER_SIZE_3)
sensor.set_gas_heater_status(False)

# MQTT Setup
BROKER = "mqtt.thingsboard.cloud"
PORT = 1883
DEVICE_TOKEN = "" #Enter device token

client = mqtt.Client()
client.username_pw_set(DEVICE_TOKEN)

def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        print("Connected to ThingsBoard successfully!")
    else:
        print(f"Failed to connect, Reason Code: {reason_code}")

def on_publish(client, userdata, mid, properties=None):
    print(f"Message {mid} published successfully.")

client.on_connect = on_connect
client.on_publish = on_publish

client.connect(BROKER, PORT, 60)
client.loop_start()

# Temperature threshold setup
temperature_threshold = 28  

# Button debounce time
DEBOUNCE_TIME = 0.2 
last_button_time = time.time()  

# Function to send email alerts
def send_email_alert(subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())

        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Function to adjust the temperature threshold using buttons
def adjust_threshold():
    global temperature_threshold, last_button_time 
    current_time = time.time()
    
    # Increase threshold when the increase button is pressed
    if GPIO.input(INCREASE_BUTTON_PIN) == GPIO.LOW and (current_time - last_button_time) > DEBOUNCE_TIME:
        temperature_threshold += 1  
        last_button_time = current_time  
        print(f"Threshold increased to: {temperature_threshold}°C")
        send_email_alert("Temperature Threshold Increased", f"The temperature threshold has been increased to {temperature_threshold}°C.")

    # Decrease threshold when the decrease button is pressed
    if GPIO.input(DECREASE_BUTTON_PIN) == GPIO.LOW and (current_time - last_button_time) > DEBOUNCE_TIME:
        temperature_threshold -= 1  
        last_button_time = current_time 
        print(f"Threshold decreased to: {temperature_threshold}°C")
        send_email_alert("Temperature Threshold Decreased", f"The temperature threshold has been decreased to {temperature_threshold}°C.")

# Function to send data to ThingsBoard
def send_data(temperature, humidity, motion_detected):
    payload = {
        "temperature": temperature,
        "humidity": humidity,
        "motion_detected": motion_detected
    }
    result = client.publish("v1/devices/me/telemetry", json.dumps(payload), qos=1)
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print("Data sent successfully.")
    else:
        print("Failed to send data.")

def read_temperature_and_humidity():
    try:
        if sensor.get_sensor_data():
            temperature = round(sensor.data.temperature, 2)
            humidity = round(sensor.data.humidity, 2)
            return temperature, humidity
        else:
            print("Sensor data is not available.")
            return None, None
    except RuntimeError as error:
        print(f"RuntimeError reading BME680 sensor: {error}")
        return None, None

def check_thresholds(temperature, humidity):
    if temperature > temperature_threshold:
        send_email_alert("Alert: High Temperature!", f"Temperature: {temperature}°C")
        print("Alert: High Temperature!", f"Temperature: {temperature}°C")
    if humidity < 30:
        send_email_alert("Alert: Low Humidity!", f"Humidity: {humidity}%")
        print(f"Alert: Low Humidity!", f"Humidity: {humidity}%")

# Motion detection debounce and delay settings
DEBOUNCE_TIME_MOTION = 1 
last_motion_time = 0

def check_motion():
    global last_motion_time
    
    current_time = time.time()
    if GPIO.input(MOTION_SENSOR_PIN):  # Motion detected
        if current_time - last_motion_time >= DEBOUNCE_TIME_MOTION:
            print("Motion detected!")
            GPIO.output(LED_PIN, GPIO.HIGH)  # Turn LED on
            last_motion_time = current_time  # Update the last motion time
            send_email_alert("Motion Detected!", "Motion has been detected near the sensor!")
            return True
        else:
            # Ignoring repeated motion trigger within debounce time
            print("Ignoring repeated motion trigger.")
            return False
    else:
        GPIO.output(LED_PIN, GPIO.LOW)  # Turn LED off
        return False

print("Starting sensor readings...\n")

try:
    while True:
        adjust_threshold()  # Adjust threshold based on button press
        temperature, humidity = read_temperature_and_humidity()
        motion_detected = check_motion()

        if temperature is not None and humidity is not None:
            print(f"Temperature: {temperature}°C, Humidity: {humidity}%, Motion: {motion_detected}")
            send_data(temperature, humidity, motion_detected)
            check_thresholds(temperature, humidity)

        time.sleep(5) 

except KeyboardInterrupt:
    print("\nStopping program.")
    GPIO.cleanup()  