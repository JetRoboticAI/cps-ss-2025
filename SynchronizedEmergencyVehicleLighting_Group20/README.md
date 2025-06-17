# 🚨 Synchronized Emergency Vehicle Lighting System (MQTT + Raspberry Pi)

This project simulates a coordinated emergency lighting system using Raspberry Pi devices. When an object is detected within a certain distance, an MQTT message is published to trigger synchronized red and blue LED strobes on all subscribed clients. This system demonstrates a basic cyber-physical system for real-time communication and coordination in safety scenarios.

## 🛠️ Components

- Raspberry Pi (x2 or more)
- Ultrasonic Distance Sensor (HC-SR04)
- Red and Blue LEDs
- Resistors (220Ω recommended)
- Jumper wires
- Breadboards
- MQTT Broker (e.g., Mosquitto)

## 📁 Files

### `sensor_controller.py`

- Detects distance using an ultrasonic sensor.
- If the distance is less than 30 cm, publishes `"ON"` to the MQTT topic `emergency/lights`.
- Local LEDs strobe on detection as well.

### `light_client.py`

- Subscribes to the MQTT topic `emergency/lights`.
- On receiving the `"ON"` signal, flashes the red and blue LEDs in a strobe pattern.

## 🧠 How It Works

1. The controller Pi continuously measures distance.
2. When an object is detected within a threshold (e.g., 30 cm), it sends an MQTT message: `"ON"`.
3. All subscribed clients receive the message and strobe their red and blue LEDs simultaneously.

## 🚀 Getting Started

## Install Dependencies

Run on both Raspberry Pis:

```bash
sudo apt update
sudo apt install python3-pip
pip3 install paho-mqtt RPi.GPIO
```
