# Smart Kitchen Ingredient Dispensing System

An IoT-based modular system that automates the accurate dispensing of encapsulated ingredients in restaurant or commercial kitchens. The system aims to streamline food preparation, reduce manual errors, and improve efficiency using ESP32-controlled dispenser units connected wirelessly to a central order manager.

---

## Project Overview

In commercial kitchens, manual ingredient preparation introduces errors, inefficiencies, and delays — especially during peak hours. This project provides a **cyber-physical solution** with:

* A **central controller** (Raspberry Pi or PC) for order management and coordination.
* Modular **dispenser units**, each handling one type of encapsulated ingredient.
* **Wireless communication** using MQTT over Wi-Fi.
* Data logging for ingredient usage, errors, and operational metrics.

---

## Objectives

* Design and prototype a smart dispenser for solid, encapsulated ingredients.
* Use sensors to detect occupancy and manage queuing when dispensing is blocked.
* Build a central system to receive simulated meal orders and delegate commands.
* Support wireless task distribution and collect usage data for planning and scaling.
* Evaluate scalability and system robustness with multiple synchronized dispensers.

---

## System Architecture

### 1. **Dispenser Unit (ESP32-based)**

* **Motor-Controlled Gate**: Servo or stepper motor to release one or more units.
* **Sensor**: IR or ultrasonic to detect if a cup or container is present.
* **Communication**: Wi-Fi via ESP32.
* **Queue Handling**: Waits if the space below is occupied.

### 2. **Central Controller**

* Receives orders (via CLI, web interface, or script).
* Parses recipes and dispatches ingredient-specific instructions.
* Manages global order queues.
* Collects logs and performance data.

### 3. **Wireless Communication**

* MQTT protocol (preferred) over Wi-Fi for low-latency and scalable messaging.
* Each dispenser subscribes to a unique topic for ingredient commands.

---

## Technologies & Components

| Category             | Details                                    |
| -------------------- | ------------------------------------------ |
| Microcontroller      | ESP32                                      |
| Sensors              | IR Proximity, Ultrasonic                   |
| Motors               | Servo or Stepper                           |
| Communication        | MQTT over Wi-Fi                            |
| Central Controller   | Raspberry Pi / Laptop                      |
| Dispensing Mechanism | 3D-Printed Modular Gate                    |
| Data Storage         | SD Card / Local file logs / Optional cloud |

---

## Getting Started

1. **Git**
   ```sh
   git clone https://github.com/Deuce-Cao/SmartKitchenIngredientDispensingSystem.git
   ```
2. Install [PlatformIO extension](https://platformio.org/install/ide?install=vscode). 
3. Modify [platformio.ini](/platformio.ini) to match the COM ports in your environment. 
4. Replace your WiFi SSID and MQTT Broker in [config.h](/src/config.h).
5. **Upload**
   ```sh
   pio run -t upload
   ```

---

## Contributors

* [Hongqing Cao](https://www.github.com/Deuce-Cao)
* Sushant Shailesh Panchal
* Yanyi He
* Yash Parab
