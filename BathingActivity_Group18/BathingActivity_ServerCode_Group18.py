import time
import paho.mqtt.client as paho
from paho import mqtt
from queue import Queue
import json
import sqlite3

payload = ""
connection = sqlite3.connect("SEP769-Prod.db")
cursor = connection.cursor()

# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)

# with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
    print("mid: " + str(mid))

# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    global payload
    payload = str(msg.payload.decode("utf-8"))
    print(payload)
    payload = json.loads(payload)
    if len(payload) > 0:
        writeToDB(payload)
    time.sleep(1)
    payload=""

def writeToDB(data):
    deviceID = data['deviceID']
    sentDate = data['sentDate']
    startDate = data['startDate']
    endDate = data['endDate']
    duration = data['duration']
    status = data['status']

    cursor.execute("""
    INSERT INTO statusData (deviceID, sentDate, startDate, endDate, duration, status) VALUES (?, ?, ?, ?, ?, ?)
    """, (deviceID, sentDate, startDate, endDate, duration, status))

    # Commit the changes
    connection.commit()
    print("Written to DB")

# using MQTT version 5 here, for 3.1.1: MQTTv311, 3.1: MQTTv31
# userdata is user defined data of any type, updated by user_data_set()
# client_id is the given name of the client
client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
client.on_connect = on_connect

# enable TLS for secure connection
client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
# set username and password
client.username_pw_set("admin", "Juliusz1")
# connect to HiveMQ Cloud on port 8883 (default for MQTT)
client.connect("7aff767b8eb4404caa62e70013948ca1.s1.eu.hivemq.cloud", 8883)

# setting callbacks, use separate functions like above for better visibility
client.on_subscribe = on_subscribe

client.on_message = on_message
client.on_publish = on_publish

# subscribe to all topics of encyclopedia by using the wildcard "#"
client.subscribe("SEP769BathCheck", qos=2)



# a single publish, this can also be done in loops, etc.
#client.publish("encyclopedia/temperature", payload="hot", qos=1)

# you can also use loop_start and loop_stop
client.loop_forever()
connection.close()