# Smart Parking Lot Management System Group 12

This project is an IoT-based smart parking lot management system. It consists of two main components:

- `769 proj parking lot group 12.py`: The script that run on Raspberry Pi devices, responsible for interacting with sensors (e.g., RFID, ultrasonic) and communicating with the backend via MQTT.
- `backend/`: Contains the Flask-based backend server for managing database.

---

## Run Raspberry Pi Scripts

Make sure your Raspberry Pi has the necessary libraries and tools installed:

```
pip install RPi.GPIO
pip install mfrc522
pip install paho-mqtt
sudo apt install -y python3-pip python3-smbus python3-gpiozero i2c-tools
```
---

## Run Backend Server
Use the following commands:
```
cd backend
pip install -r requirements.txt
python app.py
```
