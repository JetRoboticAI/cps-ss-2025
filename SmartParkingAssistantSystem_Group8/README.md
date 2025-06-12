## 📁 Project File Descriptions

This project consists of three main components: two Python scripts running on a Raspberry Pi and one HTML file for the user interface.

---

### 🐍 `create_database_sql_raspberryPi.py`

- **Location**: Raspberry Pi
- **Purpose**: Create and initialize a local SQLite database
- **Details**:
  - Creates a database named `parking_data.db`
  - Sets up a table to store:
    - Distance values from the ultrasonic sensor
    - Timestamps of measurements
    - LED status (`green`, `yellow`, or `red`) indicating proximity level

---

### 🐍 `smart_parking_raspberryPi.py`

- **Location**: Raspberry Pi
- **Purpose**: Core logic of the smart parking assistant
- **Key Functions**:
  - Reads distance from an ultrasonic sensor (HC-SR04)
  - Controls LED traffic lights to provide visual feedback
  - Publishes real-time sensor data to PubNub channel `parking.current`
  - Responds to user requests by publishing historical data to `parking.history` when `"command": "history"` is received via `parking.request` channel
  - Logs distance, timestamp, and LED status to the database **only** when the LED color changes

---

### 🌐 `user_page.html`

- **Location**: Client-side (browser)
- **Purpose**: User dashboard for monitoring parking data
- **Features**:
  - Displays real-time distance, timestamp, and LED status received from PubNub (`parking.current`)
  - Includes a button to request and display the latest 20 historical entries (`parking.history`)
  - Visual styling highlights LED status using color-coded labels

---