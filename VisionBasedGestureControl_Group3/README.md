
# 🤖 Gesture-Controlled Robotic Arm – Group 4

This project demonstrates a real-time gesture-controlled robotic system using the **Yahboom DOFBOT**, **Raspberry Pi 5**, **OpenCV**, **ROS**, and a **Support Vector Machine (SVM)** classifier. Hand gestures (1, 2, or 3 fingers) are detected by a camera and used to trigger robotic movements such as pick, wave, or reset.

---

## 📌 Features

- Real-time hand gesture recognition using OpenCV
- Lightweight SVM model trained on custom hand image dataset
- ROS-based architecture for modular communication
- DOFBOT arm controlled using Yahboom Arm_Lib library
- Fully implemented on Raspberry Pi 5

---

## 🧩 Hardware Used

- ✅ Yahboom DOFBOT 6-DOF robotic arm  
- ✅ Raspberry Pi 5 (with Raspberry Pi OS 64-bit)  
- ✅ USB or CSI camera (110° FoV recommended)  
- ✅ Power supply and servo expansion board  

---

## 💻 Software Stack

- Python 3  
- OpenCV  
- scikit-learn (SVM classifier)  
- ROS (Robot Operating System – e.g., ROS Noetic)  
- Arm_Lib for robotic control  

---

## 🛠 How It Works

1. The camera captures live video and isolates the hand region.
2. The pre-trained SVM model classifies the hand gesture (1, 2, or 3).
3. The result is published on the `/gesture_id` ROS topic.
4. The robot control node listens to this topic and triggers the appropriate robot motion.

---

## 📂 Project Structure

```
GestureControlledArm_Group4/
├── config/
│   └── model.pkl               # Trained SVM gesture classifier
├── scripts/
│   ├── gesture_detect.py       # ROS node: gesture recognition and publishing
│   └── robot_behavior.py       # ROS node: robot behavior subscriber
├── data/
│   ├── one/                    # Training images for 1-finger gesture
│   ├── two/                    # Training images for 2-finger gesture
│   └── three/                  # Training images for 3-finger gesture
├── gesture_train.py            # SVM training script
├── launch/
│   └── gesture_control.launch  # Launch file for both nodes
└── README.md                   # This file
```

---

## 🚀 Setup & Execution

### 1. Install Dependencies

```bash
sudo apt update
sudo apt install python3-opencv python3-pip
pip3 install scikit-learn joblib
```

Make sure ROS is installed and sourced, and `Arm_Lib` is set up.

---

### 2. Train Model (Optional)

If you want to retrain the model:

```bash
python3 gesture_train.py
```

---

### 3. Run the Project

In one terminal:

```bash
roscore
```

In another terminal:

```bash
roslaunch dofbot_gesture_control gesture_control.launch
```

---

## ✋ Gesture Mapping

| Gesture | ID | Robot Action       |
|---------|----|--------------------|
| 1 Finger | 1 | Pick Object        |
| 2 Fingers | 2 | Wave Motion        |
| 3 Fingers | 3 | Reset Position     |

---



## 🧪 Team Members – Group 4

Mahya
Marine
Aryan

---

## 📄 License

This project is for academic use under the MIT License.

