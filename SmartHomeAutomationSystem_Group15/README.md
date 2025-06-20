# Smart Home Automation System for Environmental Control and Motion Detection

## Overview
This project uses a Raspberry Pi with a BME680 sensor, PIR motion sensor, and MQTT to monitor environmental conditions such as temperature, humidity, and motion. Users can adjust the temperature threshold via buttons, and alerts are sent via email. The data is also sent to ThingsBoard for monitoring.

## Requirements
- **Hardware**: Raspberry Pi, BME680 sensor, PIR motion sensor, 2 push buttons, LED
- **Software**: Python 3, `bme680`, `paho-mqtt`, `RPi.GPIO`, `smtplib`

## Setup
1. Install the required Python libraries.
2. Connect the sensors to the Raspberry Pi GPIO pins.
3. Configure the script with your email, ThingsBoard device token, and broker details.
4. Enable I2C on the Raspberry Pi.
5. Run the script to start monitoring.

## Features
- Monitors temperature and humidity from the BME680 sensor.
- Detects motion with a PIR sensor and triggers LED and email alerts.
- Allows temperature threshold adjustment using push buttons.
- Sends email alerts for high temperature, low humidity, and motion detection.
- Sends data to ThingsBoard via MQTT.

## License
MIT License