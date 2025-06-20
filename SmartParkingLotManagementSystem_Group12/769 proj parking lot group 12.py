import time
import threading
from threading import Thread
import queue
from queue import Queue
import requests as requests
import paho.mqtt.client as paho
import json
import RPi.GPIO as GPIO
from gpiozero import DistanceSensor
from mfrc522 import SimpleMFRC522
import smbus

enable_sub_flag = threading.Event() #set to true to enable garage subscribing to user dashboard iot messages.
enable_pub_flag = threading.Event() #set to true to enable garage publishing to user dashboard iot messages
start_pub_to_users = threading.Event() #set to true to trigger garage publishing to user dashboard iot messages
empty_num_lock = threading.Lock() #lock the empty space number gloal variable in the counting thread

# === LCD CONFIG ===
I2C_ADDR = 0x27
LCD_WIDTH = 16
LCD_CHR = 1
LCD_CMD = 0
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005
bus = smbus.SMBus(1)

def lcd_toggle_enable(bits):
    time.sleep(E_DELAY)
    bus.write_byte(I2C_ADDR, (bits | 0x04))
    time.sleep(E_PULSE)
    bus.write_byte(I2C_ADDR, (bits & ~0x04))
    time.sleep(E_DELAY)

def lcd_byte(bits, mode):
    bits_high = mode | (bits & 0xF0) | 0x08
    bits_low = mode | ((bits << 4) & 0xF0) | 0x08
    bus.write_byte(I2C_ADDR, bits_high)
    lcd_toggle_enable(bits_high)
    bus.write_byte(I2C_ADDR, bits_low)
    lcd_toggle_enable(bits_low)

def lcd_string(message, line):
    message = message.ljust(LCD_WIDTH, " ")
    lcd_byte(line, LCD_CMD)
    for char in message:
        lcd_byte(ord(char), LCD_CHR)

def lcd_init():
    lcd_byte(0x33, LCD_CMD)
    lcd_byte(0x32, LCD_CMD)
    lcd_byte(0x06, LCD_CMD)
    lcd_byte(0x0C, LCD_CMD)
    lcd_byte(0x28, LCD_CMD)
    lcd_byte(0x01, LCD_CMD)
    time.sleep(E_DELAY)

# === STEPPER MOTOR CONFIG ===
IN1 = 17
IN2 = 18
IN3 = 27
IN4 = 22
motor_pins = [IN1, IN2, IN3, IN4]
motor_seq = [
    [1,0,0,1],
    [1,0,0,0],
    [1,1,0,0],
    [0,1,0,0],
    [0,1,1,0],
    [0,0,1,0],
    [0,0,1,1],
    [0,0,0,1]
]

def step_motor(steps, direction=1, delay=0.001):
    for _ in range(steps):
        for step in (motor_seq if direction > 0 else reversed(motor_seq)):
            for i in range(4):
                GPIO.output(motor_pins[i], step[i])
            time.sleep(delay)

# === BUTTONS CONFIG ===
YES_BUTTON = 5
NO_BUTTON = 6

# === SETUP ===
GPIO.setmode(GPIO.BCM)
GPIO.setup([YES_BUTTON, NO_BUTTON], GPIO.IN, pull_up_down=GPIO.PUD_UP)
for pin in motor_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 0)
lcd_init()
enable_pub_flag.set()
enable_sub_flag.set()
start_pub_to_users.clear()
empty_num = 0 # empty space number

# === DISTANCE SENSORS ===
sensor1 = DistanceSensor(echo=27, trigger=17)
sensor2 = DistanceSensor(echo=24, trigger=23)
sensor3 = DistanceSensor(echo=26, trigger=19)

reader = SimpleMFRC522()
scanning = True

# === Main Loops ===
def scan_parking_loop():
    global empty_num
    with empty_num_lock:
        count = 0
        while True:
            count += 1
            if count >= 5:
                start_pub_to_users.set()
                count = 0

            if scanning:
                d1 = sensor1.distance * 100
                d2 = sensor2.distance * 100
                d3 = sensor3.distance * 100
                free = 0
                if d1 > 15: free += 1
                if d2 > 15: free += 1
                if d3 > 15: free += 1
                empty_num = free
                print(f"[Parking] Free spots: {free}")
            time.sleep(1.0)

# === Utilities functions ===
DB_API_headers = {
    "X-Device-ID": "raspberrypi-02",
    "X-API-Key": "zZSp42KGfRjzdQaT",
    "Content-Type": "application/json"
}

def query_users():
    print("Query users")
    DB_result = requests.get("https://parking-api-cwtk.onrender.com/api/users", headers=DB_API_headers).json()
    print("Query result:", DB_result)
    return DB_result

def query_single_user(rfid):
    print("Query single user")
    data= {
        "rfid": rfid
        }
    DB_result = requests.post("https://parking-api-cwtk.onrender.com/api/query_user", headers=DB_API_headers, json=data).json()
    print("Query result:", DB_result)
    return DB_result

def updateDB_retrieve(rfid):
    print("Update DB for retrieval")
    data= {
        "rfid": rfid
        }
    DB_result = requests.post("https://parking-api-cwtk.onrender.com/api/unpark", headers=DB_API_headers, json=data).json()
    print("DB update result:", DB_result)
    return DB_result

def updateDB_park(rfid):
    print("Update DB for parking car")
    data= {
        "rfid": rfid
        }
    DB_result = requests.post("https://parking-api-cwtk.onrender.com/api/park", headers=DB_API_headers, json=data).json()
    print("DB update result:", DB_result)
    return DB_result

pub_ready = False
def on_connect_pub(client, userdata, flags, rc):
    global pub_ready
    print('[on_connect_pub]: CONNACK received with code %d.' % (rc))
    pub_ready = True
    
def on_connect_sub(client, userdata, flags, rc):
    print('[on_connect_sub]: CONNACK received with code %d.' % (rc))
    client.subscribe('garage_topic/#', qos=2)

def on_publish(client, userdata, mid):
    print("[on_publish]: mid: "+str(mid))

def on_subscribe(client, userdata, mid, granted_qos):
    print("[on_subscribe]: Subscribed: "+str(mid)+" "+str(granted_qos))

def on_message_sub(client, userdata, msg):
    # print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))  
    content = msg.payload.decode() #for json payload
    print(msg.topic+" "+str(msg.qos)+" "+content)  
    data = json.loads(content)
    if "retrieve" in data:
        # messages sent by user to retrieve car
        rfid = data["sender"]
        retrieve_car(rfid)
    else:
        # messages sent from garage to user
        # do nothing
        pass

def retrieve_car(rfid):
    db_result = query_single_user(rfid)
    if db_result is not None:
        if "error" in db_result:
            print("[retrieve_car]: Error: " + db_result["error"])
            lcd_string("Please contact", LCD_LINE_1)
            lcd_string("our office", LCD_LINE_2)
        else:
            if "parked" in db_result:
                if db_result["parked"] is True:
                    spot_id = db_result["spot"]
                    # assume the spot id of the car is used in reality
                    updateDB_retrieve(rfid)
                    print("[retrieve_car]: [Action] Retrieving (CCW)")
                    lcd_string("Retrieving...", LCD_LINE_1)
                    step_motor(512, direction=-1)
                    # publish refresh to all user dashboards
                    start_pub_to_users.set()
                else:
                    print("[retrieve_car]: This user's car is not parked here")
                    lcd_string("Your car is", LCD_LINE_1)
                    lcd_string("not here", LCD_LINE_2)

def park_car(rfid):
    db_result = query_single_user(rfid)
    if db_result is not None:
        if "error" in db_result:
            print("[park_car]: Error: " + db_result["error"])
            lcd_string("Please contact", LCD_LINE_1)
            lcd_string("our office", LCD_LINE_2)
        else:
            if "parked" in db_result:
                if db_result["parked"] is False:
                    updateDB_park(rfid)
                    print("[park_car] Parking (CW)")
                    lcd_string("Parking...", LCD_LINE_1)
                    step_motor(512, direction=1)
                    # publish refresh to all user dashboards
                    start_pub_to_users.set()
                else:
                    print("[park_car]: This user already has a car parked here")
                    lcd_string("Your car is", LCD_LINE_1)
                    lcd_string("already parked", LCD_LINE_2)

def garage_subscribe_retrieve():
    while enable_sub_flag.is_set():
        try:
            client = paho.Client()
            client.on_connect = on_connect_sub
            # client.on_publish = on_publish
            client.on_subscribe = on_subscribe
            client.on_message = on_message_sub
            client.tls_set()
            client.username_pw_set('garage', 'S769g12g')
            client.connect('10b91c46d29a4848b606264e0557d3eb.s1.eu.hivemq.cloud', 8883)

            client.loop_start()
            time.sleep(1)

            print("[garage_subscribe_retrieve]: Wait to receive messages")
            try:
                while enable_sub_flag.is_set():
                    time.sleep(1)
            finally:
                client.loop_stop()
                client.disconnect()
                print("[garage_subscribe_retrieve]: disconnected")
        
        except Exception as e:
            print(f"[garage_subscribe_retrieve]: Garage subcribe error: {e}")
            client.loop_stop()
            client.disconnect()
            time.sleep(0.01)
    
def garage_publish():
    global empty_num
    global pub_ready
    pub_ready = False
    while enable_pub_flag.is_set():
        try:
            client = paho.Client()
            client.on_connect = on_connect_pub
            client.on_publish = on_publish
            # client.on_subscribe = on_subscribe
            # client.on_message = on_message_sub
            client.tls_set()
            client.username_pw_set('garage', 'S769g12g')
            client.connect('10b91c46d29a4848b606264e0557d3eb.s1.eu.hivemq.cloud', 8883)

            client.loop_start()
            time.sleep(1)

            print("[garage_publish]: Waiting for start_pub_to_users set to publish")
            print("[garage_publish]: pub_ready is ", pub_ready)
            if pub_ready is True:
                while enable_pub_flag.is_set():
                    # garage publish is triggered by other events
                    if start_pub_to_users.is_set():
                        user_list = query_users()
                        if user_list is not None:
                            for user_info in user_list:
                                user_topic_branch = user_info["rfid"]
                                user_car_stored = user_info["is_parked"]
                                payload = json.dumps({'sender': 'garage', 'g1empty': str(empty_num), 'yourcarstored': "yes" if user_car_stored else "no"})
                                user_topic_path = "garage_topic/"+user_topic_branch+"/display"
                                msg_info = client.publish(user_topic_path, payload, qos=2)

                                if msg_info.is_published() == False:
                                    print('[garage_publish]: Message is not yet published.')

                                # This call will block until the message is published.
                                msg_info.wait_for_publish()
                                print("[garage_publish]: message published to topic ", user_topic_path)
                        start_pub_to_users.clear()
                    time.sleep(0.1)
                    
            client.loop_stop()
            client.disconnect()
            print("[garage_publish]: disconnected")
        
        except Exception as e:
            print(f"[garage_publish]: Garage publish error: {e}")
            client.loop_stop()
            client.disconnect()
            time.sleep(0.01)

# === Start threads ===
Thread(target=scan_parking_loop, daemon=True).start()
Thread(target=garage_subscribe_retrieve, daemon=True).start()
Thread(target=garage_publish, daemon=True).start()

# try:
#     while True:
#         start_pub_to_users.set()
#         empty_num += 1
#         if empty_num >= 3:
#             empty_num = 0
#         time.sleep(15)
#         park_car("290522920851")
#         time.sleep(15)
#         park_car("839540733898")
#         time.sleep(30)
            

# except KeyboardInterrupt:
#     enable_pub_flag.clear()
#     enable_sub_flag.clear()

#park_car("305196777043")
#retrieve_car("305196777043")


try:
    while True:
        # Check RFID every 0.1 sec
        id, text = reader.read_no_block()
        if id:
            scanning = False  # Pause sensor scanning
            print(f"[RFID] Card Detected: {id}")
            lcd_string("Welcome!", LCD_LINE_1)
            lcd_string("Park? YES/NO", LCD_LINE_2)

            # Wait for button press
            while True:
                if GPIO.input(YES_BUTTON) == GPIO.LOW:
                    park_car(str(id))
#                     print("[Action] Parking (CW)")
#                     lcd_string("Parking...", LCD_LINE_1)
#                     step_motor(512, direction=1)
                    break
                elif GPIO.input(NO_BUTTON) == GPIO.LOW:
                    retrieve_car(str(id))
#                     print("[Action] Retrieving (CCW)")
#                     lcd_string("Retrieving...", LCD_LINE_1)
#                     step_motor(512, direction=-1)
                    break
                time.sleep(0.1)

            time.sleep(2)
            lcd_string("Welcome!", LCD_LINE_1)
            lcd_string("Park? YES/NO", LCD_LINE_2)
            time.sleep(1)
            lcd_string("System ready", LCD_LINE_1)
            lcd_string("", LCD_LINE_2)
            scanning = True  # Resume scanning

        time.sleep(0.1)

except KeyboardInterrupt:
    GPIO.cleanup()
