#include <Arduino.h>
#include <Servo.h>

// Create two Servo objects for controlling two servos
Servo myServo1;
Servo myServo2;

// Pin assignments
const int servoPin1 = 9;
const int servoPin2 = 10;
const int reedPin = 2;      // Reed switch for door state
const int buzzerPin = 6;    // Buzzer for alarm

// Variables for alarm logic
unsigned long magnetRemovedTime = 0; // Time when door was opened
bool magnetAbsent = false;           // True if door is open
bool alarmSent = false;              // True if alarm has been triggered
bool buzzerSilenced = false;         // True if buzzer has been silenced

void setup() {
  // Attach servos to their pins and set initial position
  myServo1.attach(servoPin1); 
  myServo2.attach(servoPin2);
  myServo1.write(0);
  myServo2.write(0);
  
  // Set up reed switch and buzzer pins
  pinMode(reedPin, INPUT_PULLUP);
  pinMode(buzzerPin, OUTPUT);
  digitalWrite(buzzerPin, LOW);

  // Start serial communication
  Serial.begin(9600);
}

void loop() {
  // === Serial command handling ===
  if (Serial.available()) {
    char cmd = Serial.read();
    
    if (cmd == '1') {
      myServo1.write(90);  // Unlock door (servo 1 to 90 degrees)
    } else if (cmd == '0') {
      myServo1.write(0);   // Lock door (servo 1 to 0 degrees)
    } else if (cmd == '6') {
      myServo2.write(180); // Move servo 2 to 180 degrees
      delay(500);
      myServo2.write(0);   // Return servo 2 to 0 degrees
    } else if (cmd == '7') {
      buzzerSilenced = true;         // Silence the buzzer
      digitalWrite(buzzerPin, LOW);  // Turn off buzzer
    }
  }

  // === Door state monitoring ===
  bool reedState = digitalRead(reedPin);

  if (reedState == HIGH) {  // Door is open (magnet absent)
    if (!magnetAbsent) {
      magnetAbsent = true;
      magnetRemovedTime = millis(); // Record time when door opened
      alarmSent = false;            // Reset alarm trigger
    }

    // If door has been open for 10 seconds, trigger alarm (unless silenced)
    if ((millis() - magnetRemovedTime >= 10000) && !alarmSent && !buzzerSilenced) {
      digitalWrite(buzzerPin, HIGH);      // Turn on buzzer
      Serial.println("ALARM_TRIGGERED");  // Send alarm message
      alarmSent = true;                   // Mark alarm as sent
    }

    // Send "Door Opened" message every second while door is open
    static unsigned long lastSent = 0;
    if (millis() - lastSent >= 1000) {
      Serial.println("Door Opened");
      lastSent = millis();
    }

  } else {  // Door is closed (magnet present)
    if (magnetAbsent) {
      Serial.println("Door Closed"); // Send "Door Closed" message once
    }
    magnetAbsent = false;            // Reset door open flag
    digitalWrite(buzzerPin, LOW);    // Turn off buzzer
    alarmSent = false;               // Reset alarm trigger
    buzzerSilenced = false;          // Reset buzzer silence when door closes
  }
}
