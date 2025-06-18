# RFID Medication Tracker

A Python-based smart medication tracking system using RFID technology and Telegram integration to promote medication adherence and remote monitoring.

## 📌 Features

* 🏷️ **RFID Tag Recognition**
  Automatically identifies medication containers using RFID tags.

* 💾 **Medication Database**
  Centralized storage for medication names, dosages, and schedules.

* ⏰ **Medication Scheduler**
  Enables users or caregivers to set up daily medication plans.

* 📋 **Usage Logger**
  Tracks each medication interaction and logs it with timestamp.

* 📲 **Telegram Notifications**
  Sends real-time reminders and usage updates via Telegram bot.

## 🧱 Project Structure

```
sep769_rfid_medication_tracker/
│
├── config.py                  # Configuration file (paths, keys, etc.)
├── main.py                    # Main entry script
├── medication_db.py          # Handles medication records
├── medication_logger.py      # Logs usage data
├── medication_scheduler.py   # Manages scheduling and reminders
├── rfid_reader.py            # Interfaces with RFID reader hardware
├── telegram_bot_server.py    # Receives and processes Telegram commands
├── telegram_notifier.py      # Sends Telegram messages
├── utils/                    # Utility functions (if any)
└── requirements.txt          # Python dependencies
```

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/CynthiaaLee/sep769_rfid_medication_tracker.git
cd sep769_rfid_medication_tracker
```

### 2. Set Up the Environment

Create a virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure the System

Edit `config.py` to:

* Set your Telegram Bot API key
* Provide paths to your medication DB and log files
* Set up RFID device parameters

### 4. Run the Application

Start the main script:

```bash
python main.py
```

Or run individual components for testing:

```bash
python rfid_reader.py
python telegram_bot_server.py
```

## 📡 Telegram Bot

To receive notifications:

1. Create a Telegram bot via [@BotFather](https://t.me/BotFather)
2. Replace the API key in `config.py`
3. Start chatting with your bot and it will respond with reminders or logs

## 🧪 Hardware Requirements

* Raspberry Pi (or similar microcontroller)
* RFID Reader module (e.g., MFRC522)
* RFID tags (one per medication container)

## 🔐 Security Notes

* Ensure sensitive data like API keys are stored securely (e.g., using `.env` files or secret managers).
* Add authentication to prevent unauthorized use of the Telegram bot if deployed widely.

## 📄 License

This project is licensed under the MIT License.