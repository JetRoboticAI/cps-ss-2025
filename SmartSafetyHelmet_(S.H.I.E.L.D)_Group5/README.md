
# 🛡️ S.H.I.E.L.D - Smart Helmet IoT-based Emergency Localization Device

## Overview

S.H.I.E.L.D is a Raspberry Pi-based smart safety helmet system designed to monitor worker safety in hazardous environments. It integrates multiple sensors to detect falls, measure environmental conditions, and provide location data. Real-time alerts are sent to a dashboard using MQTT via Ubidots, ensuring rapid response in case of emergencies.

## Features

- **Fall Detection** using MPU6050 and a machine learning model (Random Forest)
- **Environmental Monitoring** with:
  - DHT11 for temperature and humidity
  - MQ2 for gas leakage
- **Real-time Location Tracking** using a GPS module
- **Alerts** using:
  - Buzzer
  - RGB LED for status indication
  - Vibration motor
- **Secure MQTT Communication** to Ubidots over TLS

## Hardware Components

- Raspberry Pi (any model with GPIO support)
- MPU6050 (Accelerometer + Gyroscope)
- DHT11 (Temperature and Humidity Sensor)
- MQ2 Gas Sensor
- GPS Module (e.g., NEO-6M)
- RGB LED
- Buzzer
- Vibration Motor
- Jumper Wires and Power Supply

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/<your-username>/smart-helmet-shield.git
   cd smart-helmet-shield
   ```

2. **Install Dependencies**
   ```bash
   sudo apt update
   pip install joblib numpy adafruit-circuitpython-gps paho-mqtt Adafruit_DHT
   ```

3. **Setup Ubidots Token**
   - Replace the `TOKEN` variable in the script with your actual Ubidots account token.

4. **Place the ML Model**
   - Copy your trained fall detection model (e.g., `fall_detection_rf_model.pkl`) to:
     ```
     /home/pi/Desktop/Code Files/
     ```

## Running the Code

Run the main script:

```bash
python3 Group5_S.H.I.E.L.D_Project_Final_Code.py
```

Make sure the sensors are properly connected and the ML model path is valid.

## Machine Learning for Fall Detection

The fall detection model uses a Random Forest classifier trained on data from the MPU6050 sensor. Input features include normalized acceleration and gyroscope values on all 3 axes (X, Y, Z).

Model training and evaluation are included in the `Fall_Detection Code_RandomForestClassifier.ipynb` notebook.

## Data Dashboard (Ubidots)

Sensor data and alerts are published to [Ubidots](https://industrial.ubidots.com/) for visualization and remote monitoring.

Each message includes:
- Acceleration and gyroscope values
- Fall detection status
- Temperature & humidity
- Gas leak status
- GPS coordinates

## System Status Indication (RGB LED)

| Color  | Status              |
|--------|---------------------|
| Red    | Fall detected       |
| Blue   | Gas detected        |
| Green  | Normal condition    |

## Authors

- Suraj Ramesh 
- Vipin Chandran Muthirikkaparambil	
- Chris Xavier M
- Purva Singh


**Note:** This is an academic project built for demonstration and research purposes. For industrial use, thorough testing and validation are required.
