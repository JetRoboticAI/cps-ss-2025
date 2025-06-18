import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

GPIO.setup(6, GPIO.OUT, initial=GPIO.LOW)
#GPIO.output(6, GPIO.LOW)

GPIO.setup(17, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(27, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(22, GPIO.OUT, initial=GPIO.HIGH)
GPIO.cleanup()