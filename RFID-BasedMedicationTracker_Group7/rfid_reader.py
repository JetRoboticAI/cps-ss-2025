# -*- coding: utf-8 -*-
"""
@Author: Jieying Li
@Created Date: 2025-05-27 21:58:46
@Path: /rfid_reader.py
"""

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

def read_rfid():
    try:
        print("Please place your RFID card near the reader...")
        id, _ = reader.read()
        print(f"Card UID: {id}")
        return str(id).strip()  # Return UID as a string without extra spaces
    except KeyboardInterrupt:
        print("Program interrupted.")
        return None
    finally:
        GPIO.cleanup()