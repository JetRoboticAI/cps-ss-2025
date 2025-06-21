# 🏠 Smart Door Monitoring System

This project is a smart system that lets you **lock/unlock a door**, **close it remotely**, and **get alerts** if the door is left open. It uses an **Arduino** and a **Raspberry Pi**, and connects to your laptop and phone using the **Blynk** app.

---

## ✅ What It Can Do

- 🔐 Lock and unlock the door 
- 🚪 Detect if the door is open or closed  
- 🔊 Sound an alarm if the door stays open too long  
- 📲 Send updates to your phone in real-time  
- 📝 Save logs of every door and lock action  

---

## 🧰 What You Need

- Arduino Uno  
- Raspberry Pi (4GB RAM) with Wi-Fi  
- 2x Servo motors (Model SG90)  
- Magnetic reed switch (Model KY-021) 
- Active Buzzer (KY-012)  
- USB drive for logs  
- Jumper wires (Male-Male, Male-Female)
- Power supply (5V)  

---

## 🔌 How It Works

- The **Arduino** checks the door sensor and controls the motors and buzzer  
- The **Raspberry Pi** talks to the Arduino and sends updates to your phone  
- You control the system with the **Blynk app**  

---

## 🖱️ Blynk Controls

| Control | What it Does |
|--------|----------------|
| V0     | Lock/unlock door |
| V1     | Show lock status |
| V2     | Silence the alarm |
| V3     | Show door open/closed |
| V4     | Close the door |
| V5     | Show alarm messages |

---

## 📂 Files in This Project

- `ArduinoCode.cpp`: Code for the Arduino (controls motors and buzzer)  
- `RaspberryPiCode.py`: Code for the Raspberry Pi (sends data to phone and logs actions)  

---

## 🛠️ Setup Steps

1. Use the Arduino board to power and ground a breadboard
2. Connect each sensor, actuator and buzzer to its corresponding PWM pin found in the Arduino code
3. Ground each component
4. Upload `ArduinoCode.cpp` to your Arduino
5. Connect the Arduino to the Raspberry Pi via USB serial communication
6. Run `RaspberryPiCode.py` on your Raspberry Pi
7. Set up the Blynk app using the correct virtual pins
8. Watch your door updates live from your phone!

---

## 💡 Future Ideas

- Add voice assistant support (Alexa, Google)  
- Store logs online (cloud-based) instead of USB  
- Add geofencing to lock/unlock automatically when phone is nearby
- Add battery backup in case power goes out  

---

If you want help or more info, check out the PDFs in this project!