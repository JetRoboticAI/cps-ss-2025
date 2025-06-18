import RPi.GPIO as GPIO
# from mfrc522 import SimpleMFRC522
import time
import threading

# reader = SimpleMFRC522()
exit_event = threading.Event()  # 全局退出事件


def read_rfid():
    from mfrc522 import SimpleMFRC522
    reader = SimpleMFRC522()
    try:
        print('Please put the RFID card into the reader...')
        print(GPIO.getmode())

        while not exit_event.is_set():  # 检查退出事件
            id, text = reader.read_no_block()  # 改为非阻塞读取方法

            if id:  # 如果读取到卡片
                print(f'Read ID: {id}')
                return str(id)

            time.sleep(0.5)  # 每次循环等待 0.5 秒以减轻 CPU 占用

        return None  # 如果退出事件被触发，返回 None

    except Exception as e:
        print(f"RFID read error: {e}")
        return None

#     finally:
#         GPIO.cleanup()
