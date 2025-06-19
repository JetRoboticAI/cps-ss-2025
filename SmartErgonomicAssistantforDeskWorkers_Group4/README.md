# Smart Ergonomic Assistant for Desk Workers

Prolonged sitting with poor posture and insufficient breaks has become a significant health concern for office employees and remote workers. This paper presents the design and implementation of a Smart Ergonomic Assistant using a Raspberry Pi that promotes healthier desk habits. The system monitors posture and screen distance using ultrasonic sensors, provides real-time feedback via an LCD display and RGB LEDs, and logs ergonomic events to Google Sheets for tracking and analysis. It also issues timely reminders for hydration and movement breaks, encouraging users to adopt proactive ergonomic behaviors. This low-cost, scalable solution aims to enhance digital wellness and reduce the long-term health risks associated with sedentary work environments.

## Features

- Real-time posture monitoring
- Personalized ergonomic tips
- Break reminders
- Analytics dashboard

## Installation Guide

1. **Clone the repository:**

   ```bash
   git clone https://github.com/polonium31/cps-ss-2025-Group4.git
   cd SmartErgonomicAssistantforDeskWorkers_Group4
   ```

2. **Set up the Raspberry Pi:**

   - Ensure your Raspberry Pi is running the latest version of Raspberry Pi OS.
   - Connect the ultrasonic sensors, LCD display, and RGB LEDs as described in the hardware documentation.

3. **Create and activate a Python virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install dependencies:**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. **Configure Google Sheets API:**

   - Place the `credentials.json` file in the project root directory.

6. **Run the application:**

   ```bash
   python group4_s25.py
   ```

## File Structure

```
SmartErgonomicAssistantforDeskWorkers_Group4/
├── group4_s25.py         # Main application entry point
├── lcd/                  # LCD display driver package
│   ├── drivers.py        # LCD hardware interface code
│   ├── __init__.py       # Package initializer
├── requirements.txt      # Python dependencies list
├── credentials.json      # Google Sheets API credentials
├── .gitignore            # Git ignored files configuration
```

- The main application logic starts from `group4_s25.py`.

## Contributors

- **Jainish Shaileshbhai Patel**  
   W Booth School of Engineering Practice and Technology  
   Specialization: Systems and Technology - Automation Smart System  
   McMaster University, Hamilton, Canada (Zip Code L8S 4L8)

- **Mayur Kalabhai Patel**  
   W Booth School of Engineering Practice and Technology  
   Specialization: Digital Manufacturing  
   McMaster University, Hamilton, Canada (Zip Code L8S 4L8)
