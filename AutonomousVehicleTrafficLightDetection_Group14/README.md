# AutonomousVehicleTrafficLightDetection_Group14

## Project Overview

This project is a Raspberry Pi–based autonomous vehicle system designed to detect traffic lights using the HuskyLens AI camera. The vehicle uses traffic light detection to make stop/go decisions, enabling intelligent traffic interaction. This project also integrates MIT App Inventor for the wireless component where the motors can be started and stopped using an app. This is visible in the videos uploaded.


## Key Features

- Real-time detection of red and green lights
- Vehicle automatically stops or moves based on detected light
- Uses UART communication between Raspberry Pi and HuskyLens
- Controlled via DC motors and motor driver module
- Motors can be controlled wirelessly through app

## Component Requirements

- Raspberry Pi
- HuskyLens AI Vision Sensor
- Motor Driver (L298N)
- 2 DC Motors
- Jumper Wires and Breadboard
- Power Supply or Battery Pack
- MIT App Inventor (Wi-Fi enabled)


## How to Run

1. Connect the HuskyLens to the Raspberry Pi via UART (TX/RX).
2. Place `main.py` and `huskylib.py` in the same directory.
3. On the Raspberry Pi terminal run:
   python3 main.py
4. Wireless component requires app to be connected via MIT APP Inventor on same Wi-Fi and press start/stop to observe changes

## Group Members - Group 14
Kushal Shah
Sarthak Paliwal
Jenil Virani