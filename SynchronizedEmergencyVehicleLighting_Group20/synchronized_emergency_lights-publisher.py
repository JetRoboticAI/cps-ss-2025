import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time

# Pins
TRIG = 23
ECHO = 24
RED = 17
BLUE = 27

# MQTT
broker = "localhost"  # or IP of broker
topic = "emergency/lights"
client = mqtt.Client()

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(RED, GPIO.OUT)
GPIO.setup(BLUE, GPIO.OUT)

def get_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        start = time.time()
    while GPIO.input(ECHO) == 1:
        end = time.time()

    return round((end - start) * 17150, 2)

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

# Callback: When a message is received
def on_message(client, userdata, message):
    if message.payload.decode() == "ON":
        strobe_lights()

client.on_message = on_message
client.connect(broker)
client.subscribe(topic)
client.loop_start()

try:
    while True:
        distance = get_distance()
        print(f"Distance: {distance} cm")
        if distance < 30:
            client.publish(topic, "ON")
        time.sleep(1)

except KeyboardInterrupt:
    GPIO.cleanup()
    client.loop_stop()