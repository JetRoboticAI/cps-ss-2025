# Group 13 – Smart Remote Monitoring & Control of Field Instrument

## 🚀 Project Overview

This project aims to enhance operational safety and efficiency during start-up, commissioning, and preventive maintenance of industrial systems by enabling **remote monitoring and control** of local gauges and Motor Operated Valves (MOVs). Using a Raspberry Pi, sensors, and stepper motor drivers, the system eliminates the need for constant manual intervention and enables real-time visibility via the **Adafruit IO Dashboard**.

---

## 🧠 Problem Statement

In industrial environments, many critical instruments like analog gauges and MOVs are not integrated into centralized control systems. Monitoring them relies on physical human presence, which:
- Increases manpower requirements
- Leads to human error and delayed responses
- Makes data logging for ML analytics infeasible

---

## 💡 Proposed Solution

A **Wi-Fi-enabled Raspberry Pi** with attached sensors and a camera provides real-time data to a cloud dashboard using **MQTT** and the **Adafruit IO** platform. Key features include:
- Remote temperature and humidity monitoring (via DHT11)
- Stepper motor control of MOVs using dashboard toggle
- Live feedback and alerts
- Expandability to camera streaming and additional sensors

---

## 🛠 Hardware Components
- Raspberry Pi 3/4
- DHT11 Sensor (Temperature & Humidity)
- Stepper Motor + Motor Driver (ULN2003 or similar)
- 9V Li-ion Battery
- Compact Camera (optional for visual monitoring)
- Breadboard, jumper wires

---

##  Software & Libraries

Install the following libraries before running the code:

```bash
pip3 install adafruit-circuitpython-dht
pip3 install adafruit-blinka
pip3 install adafruit-io
pip3 install gpiozero
```

##  Adafruit IO Credentials

Before running the script, **you must enter your Adafruit IO credentials** in the code:

```python
ADAFRUIT_IO_KEY = ''        #  Your Adafruit IO Key
ADAFRUIT_IO_USERNAME = ''    #  Your Adafruit IO Username