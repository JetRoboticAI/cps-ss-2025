import time
import board
import digitalio
from gpiozero import OutputDevice
from Adafruit_IO import Client, Feed, RequestError
import adafruit_dht

xx=1

motorPins = (18, 23, 24, 25) # define pins connected to four phase ABCD of stepper motor
# motorPins = ("J8:12", "J8:16", "J8:18", "J8:22") # define pins connected to four phase ABCD of stepper motor
motors = list(map(lambda pin: OutputDevice(pin), motorPins))
CCWStep = (0x01,0x02,0x04,0x08) # define power supply order for rotating anticlockwise 
CWStep = (0x08,0x04,0x02,0x01)  # define power supply order for rotating clockwise
     
# as for four phase stepping motor, four steps is a cycle. the function is used to drive the stepping motor clockwise or anticlockwise to take four steps    
def moveOnePeriod(direction,ms):    
    for j in range(0,4,1):      # cycle for power supply order
        for i in range(0,4,1):  # assign to each pin
            if (direction == 1):# power supply order clockwise
                motors[i].on() if (CCWStep[j] == 1<<i) else motors[i].off()
            else :              # power supply order anticlockwise
                motors[i].on() if CWStep[j] == 1<<i else motors[i].off()
        if(ms<3):       # the delay can not be less than 3ms, otherwise it will exceed speed limit of the motor
            ms = 3
        time.sleep(ms*0.001)    
        
# continuous rotation function, the parameter steps specifies the rotation cycles, every four steps is a cycle
def moveSteps(direction, ms, steps):
    for i in range(steps):
        moveOnePeriod(direction, ms)
        
# function used to stop motor
def motorStop():
    for i in range(0,4,1):
        motors.off()    

ADAFRUIT_IO_KEY = your_key_here

ADAFRUIT_IO_USERNAME = your_username_here

# Create an instance of the REST client.
aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

# Assign a temperature feed, if one exists already
try:
    temperature_feed = aio.feeds('temperaturef')
except RequestError: # Doesn't exist, create a new feed
    feed_temp = Feed(name="temperaturef")
    temperature_feed = aio.create_feed(feed_temp)

# Assign a humidity feed, if one exists already
try:
    humidity_feed = aio.feeds('humidityf')
except RequestError: # Doesn't exist, create a new feed
    feed_humid = Feed(name="humidityf")
    humidity_feed = aio.create_feed(feed_humid)

try:
    digital = aio.feeds('digital')
except RequestError:
    feed = Feed(name="digital")
    digital = aio.create_feed(feed)

led = digitalio.DigitalInOut(board.D6)
led.direction = digitalio.Direction.OUTPUT
    
    
# Uncomment for DHT11
sensor = adafruit_dht.DHT11(board.D4)

while True:
    try:
        # Print the values to the serial port
        temperature_c = sensor.temperature
        temperature_f = temperature_c * (9 / 5) + 32
        humidity = sensor.humidity
        print("Temp={0:0.1f}ºC, Temp={1:0.1f}ºF, Humidity={2:0.1f}%".format(temperature_c, temperature_f, humidity))
        aio.send(temperature_feed.key, round(temperature_c,2))
        aio.send(humidity_feed.key, round(humidity,2))
        data = aio.receive(digital.key)
        if int(data.value) == 1:
                led.value = True
                print('received <- ON\n')
                if xx==1:
                    moveSteps(0,3,512)  # rotating 360 deg clockwise, a total of 2048 steps in a circle, 512 cycles
                    time.sleep(0.5)
                    xx=0
        elif int(data.value) == 0:
                led.value = False
                print('received <- OFF\n')
                if xx==0:
                    moveSteps(1,3,512)  # rotating 360 deg anticlockwise
                    time.sleep(0.5)
                    xx=1
        
    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])
        time.sleep(2.0)
        continue
    except Exception as error:
        sensor.exit()
        raise error

    time.sleep(5)
