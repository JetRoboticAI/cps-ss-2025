import time
import RPi.GPIO as GPIO
import rfid_reader_v2 as rfid_reader
import servo_control_v2 as servo_control
import threading
from rfid_reader_v2 import exit_event
from pubnub.callbacks import SubscribeCallback
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

# PubNub Configuration
pnconfig = PNConfiguration()
pnconfig.subscribe_key = 'sub-c-a6797b99-e665-4db1-b0ec-2cb77ad995ed'
pnconfig.publish_key = 'pub-c-e478cfb1-92ef-4faa-93cc-d1c4022ecb19'
pnconfig.uuid = '321'
pubnub = PubNub(pnconfig)

# Channel names
CONTROL_CHANNEL = "MingyiHUO728"
STATUS_CHANNEL = "MingyiHUO728"

# Initialize GPIO mode
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Global variables
rfid_success = False
remote_unlock = False
card = None

def publish_status(status_data):
    status_data["message_type"] = "status"
    pubnub.publish().channel(STATUS_CHANNEL).message(status_data).sync()

class MySubscribeCallback(SubscribeCallback):
    def message(self, pubnub, message):
        global remote_unlock
        if message.channel == CONTROL_CHANNEL:
            if message.message.get('message_type') == "control" and message.message.get('action') == 'unlock':
                remote_unlock = True
                print("Remote unlock command received")
                # Handle remote unlock immediately
                servo_control.unlock()
                publish_status({
                    "state": 1,
                    "type": "remote",
                    "time": time.time(),
                    "name": "Remote Access"
                })
                # Start a timer thread to lock after 5 seconds
                lock_timer = threading.Timer(5.0, delayed_lock)
                lock_timer.start()

def delayed_lock():
    servo_control.lock()
    publish_status({
        "state": 0,
        "type": "remote",
        "time": time.time(),
        "name": "Remote Access"
    })
    print("The door has been locked!")
    global remote_unlock
    remote_unlock = False

pubnub.add_listener(MySubscribeCallback())
pubnub.subscribe().channels([CONTROL_CHANNEL]).execute()

def rfid_authentication():
    global rfid_success, card
    while not rfid_success and not remote_unlock:
        card_id = rfid_reader.read_rfid()
        print(f"Scanned card ID: {card_id}")

        if card_id is not None:
            rfid_success = True
            card = card_id
            if card_id == '860338929300':
                print('RFID verification successful')
                servo_control.unlock()
                publish_status({
                    "state": 1,
                    "type": "rfid",
                    "time": time.time(),
                    "name": card_id
                })
            else:
                print('Unauthorized card!')
                publish_status({
                    "state": 0,
                    "type": "rfid",
                    "time": time.time(),
                    "name": card_id
                })
            return

try:
    while True:
        print("Please scan your RFID card...")
        rfid_thread = threading.Thread(target=rfid_authentication)
        rfid_thread.start()
        rfid_thread.join()

        if rfid_success and card == '860338929300':
            print("The door will lock in 5 seconds!")
            time.sleep(5)
            servo_control.lock()
            publish_status({
                "state": 0,
                "type": "rfid",
                "time": time.time(),
                "name": card
            })
            print("The door has been locked!")
        
        # Reset for next scan
        rfid_success = False
        card = None
        time.sleep(1)

except KeyboardInterrupt:
    print('Program interrupted. Cleaning up GPIO settings...')

finally:
    exit_event.set()
    pubnub.unsubscribe().channels([CONTROL_CHANNEL]).execute()
    servo_control.cleanup()
    GPIO.cleanup()