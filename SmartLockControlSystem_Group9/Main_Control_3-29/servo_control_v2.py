import RPi.GPIO as GPIO
import time

# 引脚定义
SERVO_PIN = 24  # GPIO24 (BCM 模式)

servo = None  # 全局变量，伺服电机的 PWM 对象
servo_initialized = False  # 引脚初始化状态变量


def init_servo():
    global servo, servo_initialized

    if not servo_initialized:  # 确保只初始化一次
        GPIO.setup(SERVO_PIN, GPIO.OUT)
        servo = GPIO.PWM(SERVO_PIN, 50)  # 初始化 PWM (50Hz)
     
    if GPIO.getmode() is None:
        GPIO.setmode(GPIO.BCM)
    elif GPIO.getmode() == GPIO.BOARD:
        raise RuntimeError('GPIO Set Mode Error: Please use BCM mode.')

    GPIO.setwarnings(False)
    GPIO.setup(SERVO_PIN, GPIO.OUT)

    servo.start(0)
    servo_initialized = True


def unlock():
    init_servo()
    print("Unlocking...")
    servo.ChangeDutyCycle(7.5)  # 转到 90 度 (解锁)
    time.sleep(2)
    servo.ChangeDutyCycle(0)


def lock():
    init_servo()
    print("Locking...")
    servo.ChangeDutyCycle(2.5)  # 转到 0 度 (锁定)
    time.sleep(0.5)
    servo.ChangeDutyCycle(0)

def cleanup():
    global servo
    if servo:
        servo.stop()
    GPIO.cleanup()

if __name__ == '__main__':
    try:
        print("Unlocking...")
        unlock()
        print("Locking...")
        lock()
    finally:
        cleanup()
