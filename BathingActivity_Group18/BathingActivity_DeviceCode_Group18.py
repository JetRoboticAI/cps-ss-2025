import time
import paho.mqtt.client as paho
import paho.mqtt.publish as publish
from paho import mqtt
import json
import RPi.GPIO as GPIO

#bathStatus = False = low power mode, True = active shower mode]
bathStatus = False
LED_PIN = 17
SENSOR = 22
client = ""
deviceID = "25A001"

def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK RECEIVED WITH CODE %s." % rc)
    
def on_publish(client, userdata, mid, properties=None):
    print("mid: " + str(mid))

def on_subscribe(client,userdata,mid,granted_qos,properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))
    
def on_message(client,userdata,msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

def mqttConnect():
    global client
    global deviceID
    print("Connecting MQTT")
    client = paho.Client(client_id="",userdata=None, protocol=paho.MQTTv5)
    client.on_connect = on_connect
    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    client.username_pw_set("admin","Juliusz1")
    broker = "7aff767b8eb4404caa62e70013948ca1.s1.eu.hivemq.cloud"
    port = 8883
    client.connect(broker, port)
    client.loop_start()

    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.on_publish = on_publish

    #mqttPublish(deviceID,1,1,1,-1)
    print("MQTT Connected")
    #client.loop_forever()
    return client

def mqttPublish(deviceID, startDate, endDate, duration, status):
    global client
    print("publishing...")
    topic = "SEP769BathCheck"
    sentDate = time.time()
    data = {
    "deviceID": deviceID,
    "sentDate": sentDate,
    "startDate": startDate,
    "endDate": endDate,
    "duration": int(duration),
    "status": status
    }
    json_data = json.dumps(data)
    print(json_data)
    client.publish(topic,payload=json_data, qos = 2)
    print("MQTT Published")
    #client.disconnect()
    #mqttConnect()
    time.sleep(2)
    


def setup():
    
    # Set up the GPIO pin numbering mode
    GPIO.setmode(GPIO.BCM)

    # Set up the GPIO pin for the LED
    GPIO.setup(LED_PIN, GPIO.OUT)
    GPIO.output(LED_PIN, GPIO.LOW)
    
    #set up pin for doppler sensor
    GPIO.setup(SENSOR, GPIO.IN)
    print("setup complete")

def LED(value):
    global LED_PIN
    if value == 1:
        GPIO.output(LED_PIN, GPIO.HIGH)
        #time.sleep(interval)
    else:
        GPIO.output(LED_PIN, GPIO.LOW)
        #time.sleep(interval)

def doppler():
    value = GPIO.input(22)
    #print(f"Doppler Sensor: {value}")
    LED(value)
    return value
    
def statusSwitch():
    print(f"checking which mode to be in. Current Status = {bathStatus}")
    
    if bathStatus == False:
        lowPowerMode(10)
    else:
        #double check that there is someone there...
        #status = checkActivity(10,1,2,"double checking")
        #if status == True:
        bathingTime()
 

def checkActivity(checkTime, interval, threshold, msg):
    #mode -1 = false alarm, 0= low, 1= double check, 2 = active
    status = False
    count = 0
    for n in range(int(checkTime/interval)):
        value = doppler()
        #print(f"value of sensor is {value}")
        if value == 1:
            #print(f"count is {count}")   
            count = count + 1
        time.sleep(interval)
    if count > threshold:
        status = True
    else:
        status = False
    #print("end check")
    
    return status

def lowPowerMode(sleepTime):
    global bathStatus
    print(f"in low power mode - global status = {bathStatus}")
    start = time.time()
    
    #every 1 minutes check for 10 seconds if there is movement, if there is change bathStatus to True
    
    while bathStatus == False:
        print("checking")
        bathStatus = checkActivity(20,1,2, "low power mode")
        
        if bathStatus == False:
            time.sleep(sleepTime)
    
    end = time.time()
    
    #print(f"Bathing Status is {bathStatus}")
    

def bathingTime():
    global bathStatus
    global deviceID
    
    start = time.time()
    check_time = 30
    print(f"active Bathing Mode - global status = {bathStatus}") 
    while bathStatus == True:
        print("still bathing")
        bathStatus = checkActivity(check_time,1,2, "bathing time")
    
    end = time.time()
    duration = end - start
    status = 1
    mqttPublish(deviceID, start, end, duration, status)
    
    print(f"The duration of the bath is {duration}")





if __name__ == '__main__':   # Program entrance
    print("Program set up")
    setup()
    mqttConnect()
    
    print ('Program is starting ... ')
    try:
        while True:
            statusSwitch()     
    except KeyboardInterrupt: # Press ctrl-c to end the program.
        GPIO.cleanup()
        client.loop_stop()
        client.disconnect()
        print("Ending program")