import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time

# LED Pins
RED = 17
BLUE = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(RED, GPIO.OUT)
GPIO.setup(BLUE, GPIO.OUT)

def strobe_lights(times=10, delay=0.1):
    for _ in range(times):
        GPIO.output(RED, True)
        GPIO.output(BLUE, False)
        time.sleep(delay)
        GPIO.output(RED, False)
        GPIO.output(BLUE, True)
        time.sleep(delay)
    GPIO.output(RED, False)
    GPIO.output(BLUE, False)

# MQTT Callback
def on_message(client, userdata, message):
    if message.payload.decode() == "ON":
        print("Strobe signal received")
        strobe_lights()

# MQTT Setup
broker = "localhost"  # Replace with IP of the broker if remote
topic = "emergency/lights"
client = mqtt.Client()
client.connect(broker)
client.subscribe(topic)
client.on_message = on_message

client.loop_forever()