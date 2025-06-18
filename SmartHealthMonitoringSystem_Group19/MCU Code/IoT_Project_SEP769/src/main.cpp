#include <Arduino.h>
//#include <string.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <LiquidCrystal_I2C.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <time.h>
#include <ArduinoJson.h>
#include "MAX30100_PulseOximeter.h"

#define REPORTING_PERIOD_MS 1000
#define sampleTime 10000
#define avgReadings 50
#define emergencyButton 12
#define startButton 14
#define buzzerPin 13
#define MAX30100_INT_PIN 16

JsonDocument doc; //for parsing json from cloud
JsonDocument doc2; //for sending data to cloud
JsonDocument doc3; //for requesting patient
String JSONtoSend;
String requestPatientJSON;

// Connections : SCL PIN - D1 , SDA PIN - D2 , INT PIN - D0
PulseOximeter pox;

// WiFi and MQTT client initialization
BearSSL::WiFiClientSecure espClient;
PubSubClient mqtt_client(espClient);


// GPIO where the DS18B20 is connected to
const int oneWireBus = 2;  

// Setup a oneWire instance to communicate with any OneWire devices
OneWire oneWire(oneWireBus);

// Pass our oneWire reference to Dallas Temperature sensor 
DallasTemperature sensors(&oneWire);

//LCD
LiquidCrystal_I2C lcd(0x27,16,2);  // set the LCD address to 0x27 for a 16 chars and 2 line display

// WiFi credentials
const char *ssid = "power";             // Replace with your WiFi name
const char *password = "iamthebest";   // Replace with your WiFi password

// MQTT Broker settings
const int mqtt_port = 8883;  // MQTT port (TLS)
const char *mqtt_broker = "broker.emqx.io";  // EMQX broker endpoint
const char *mqtt_subscribe = "/ranaharshil/cloud";     // MQTT topic
const char *mqtt_publish = "/ranaharshil/cloud";     // MQTT topic
const char *mqtt_username = "emqx";  // MQTT username for authentication
const char *mqtt_password = "public";  // MQTT password for authentication

// NTP Server settings
const char *ntp_server = "pool.ntp.org";     // Default NTP server
const long gmt_offset_sec = 14400;            // GMT offset in seconds (adjust for your time zone)
const int daylight_offset_sec = 3600;        // Daylight saving time offset in seconds


//All function declarations
// float getMyBPM();
// float getMySpO2();
// bool checkStartButton();
// bool checkEmergencyButton();
void connectToWiFi();
void connectToMQTT();
void syncTime();
void mqttCallback(char *topic, byte *payload, unsigned int length);
void sendJSON();
// bool requestPatient();
void makeBeep();
float getMyTemp();
float getMyBPM();
float getMySpO2();

//Program Variables
unsigned long lastDebounceTime = 0; // the last time the output pin was toggled
unsigned long debounceDelay = 50; // the debounce time; increase if the output flickers
bool currentStartButtonState; // the current reading from the Startbutton pin
bool lastStartButtonState = LOW; // the previous reading from the Startbutton pin
bool emergencyState = false; //
float currentBPM = 0.0; //live BPM value
float currentSpO2 = 0.0; //live SpO2 value
float currentTemp = 0.0; //live temperature value
bool requestSent = false;
bool startButtonPressed=false;
uint8_t currentPatient = 0; //Cloud -> Local -> LCD
String healthStatus = "Error" ; //Cloud -> Local -> LCD = Depending on BPM, SpO2 and Temp send either (1)Excellent, (2)Good, (3)Average, (4)Poor
uint8_t waitingTime = 0; //Next available appointment with doctor in x mins available
uint32_t startMeasurementTime;
bool newPatient = false;
int patientID = 0;

//Emergency button intterup
IRAM_ATTR void detectsMovement() 
{
  if(!emergencyState)
  {
    Serial.println("Emergency Button Pressed");
    digitalWrite(buzzerPin, HIGH);
    emergencyState = true;
    sendJSON();
  }
  else
  {
    Serial.println("Emergency Button Released");
    digitalWrite(buzzerPin, LOW);
    emergencyState = false;
    sendJSON();
  }
  
  
  // lcd.clear();
  // lcd.setCursor(0,0);
  // lcd.print("Emergency alert");
  // lcd.setCursor(0,1);
  // lcd.print("!!!!!");
  // delay(10000);
  // digitalWrite(buzzerPin, LOW);
  // emergencyState = false;
}


void setup() {
  pinMode(buzzerPin, OUTPUT);
  digitalWrite(buzzerPin, LOW);
  pinMode(emergencyButton, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(emergencyButton), detectsMovement, RISING);
  pinMode(startButton, INPUT);
  Serial.begin(115200);
  lcd.init(); 
  lcd.backlight();
  lcd.setCursor(0,0);
  lcd.print("IoT Health");
  lcd.setCursor(0,1);
  lcd.print("Monitoring");
  delay(2000);
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("SEP769");
  lcd.setCursor(0,1);
  lcd.print("Group 19");
  delay(2000);
  connectToWiFi(); //Wifi Setup
  syncTime();  // X.509 validation requires synchronization time
  mqtt_client.setServer(mqtt_broker, mqtt_port); //MQTT Setup
  mqtt_client.setCallback(mqttCallback); //MQTT Sunscriber
  connectToMQTT(); //MQTT Connect CMD
  sensors.begin(); //Start DS18B20 Sensor
  pinMode(MAX30100_INT_PIN, OUTPUT); //INT Pin for MAX30100
  Serial.print("Initializing Pulse Oximeter..");
  if (!pox.begin())
  {
    Serial.println("FAILED");
    for(;;);
  }
  pox.shutdown();
}

void loop() {
  if (!mqtt_client.connected()) 
  {
    connectToMQTT();
  }
  

  while(!newPatient)
  {
    mqtt_client.loop();
    lcd.clear();
    lcd.setCursor(0,0);
    lcd.print("Waiting for new");
    lcd.setCursor(0,1);
    lcd.print("Patient.");
    mqtt_client.loop();
    delay(250);
    lcd.setCursor(0,1);
    lcd.print("Patient..");
    mqtt_client.loop();
    delay(250);
    lcd.setCursor(0,1);
    lcd.print("Patient...");
    delay(250);
  }
  makeBeep();
  makeBeep();
  makeBeep();
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Patient ID: ");
  lcd.print(patientID);
  lcd.setCursor(0,1);
  lcd.print("Press Start");
  while(!startButtonPressed)
  {
    startButtonPressed = digitalRead(startButton);
    delay(50);
  }
  startButtonPressed=false;
  newPatient=false;
  currentTemp = getMyTemp();
  makeBeep();
  lcd.setCursor(0,1);
  lcd.print("Measuring Heart.");
  startMeasurementTime = millis();
    pox.resume();
    while(millis() - startMeasurementTime < sampleTime)
    {
      currentBPM = getMyBPM();
      Serial.print("Heart rate:");
      Serial.print(currentBPM);
      currentSpO2 = getMySpO2();
      Serial.print("  SpO2:");
      Serial.print(currentSpO2);
      Serial.println(" %");
    }
    Serial.println("***********************");
    pox.shutdown();
    
    makeBeep();

  sendJSON();
  // Code is not entering in while loop
  while(healthStatus == "null")
  {
    mqtt_client.loop();
    lcd.clear();
    lcd.setCursor(0,0);
    lcd.print("Waiting for");
    lcd.setCursor(0,1);
    lcd.print("Reply.");
    mqtt_client.loop();
    delay(250);
    lcd.setCursor(0,1);
    lcd.print("Reply..");
    mqtt_client.loop();
    delay(250);
    lcd.setCursor(0,1);
    lcd.print("Reply...");
    delay(250);
  }
  
  makeBeep();
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Health: ");
  lcd.print(healthStatus);
  lcd.setCursor(0,1);
  lcd.print("Waiting Time:");
  lcd.print(waitingTime);
  delay(5000);
}

void syncTime() {
    configTime(gmt_offset_sec, daylight_offset_sec, ntp_server);
    Serial.print("Waiting for NTP time sync: ");
    while (time(nullptr) < 8 * 3600 * 2) {
        delay(1000);
        Serial.print(".");
    }
    Serial.println("Time synchronized");
    struct tm timeinfo;
    if (getLocalTime(&timeinfo)) {
        Serial.print("Current time: ");
        Serial.println(asctime(&timeinfo));
    } else {
        Serial.println("Failed to obtain local time");
    }
}

void connectToWiFi() {
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }
    
    Serial.println("Connected to WiFi");
    lcd.clear();
    lcd.setCursor(0,0);
    lcd.print("WiFi Connected");
    lcd.setCursor(0,1);
    uint32_t myIp = WiFi.localIP();
    lcd.print(char(myIp));
    //WiFi.localIP();
    delay(2000);

}

void connectToMQTT() {
    espClient.setInsecure();
    while (!mqtt_client.connected()) {
        String client_id = "esp8266-client-" + String(WiFi.macAddress());
        Serial.printf("Connecting to MQTT Broker as %s.....\n", client_id.c_str());
        if (mqtt_client.connect(client_id.c_str(), mqtt_username, mqtt_password)) {
            Serial.println("Connected to MQTT broker");
            mqtt_client.subscribe(mqtt_subscribe);
            // Publish message upon successful connection
            //mqtt_client.publish(mqtt_publish, "{\"System Status\":\"Paris\",\"temp\":18.5}");
        } else {
            char err_buf[128];
            espClient.getLastSSLError(err_buf, sizeof(err_buf));
            Serial.print("Failed to connect to MQTT broker, rc=");
            Serial.println(mqtt_client.state());
            Serial.print("SSL error: ");
            Serial.println(err_buf);
            delay(5000);
        }
    }
}

void mqttCallback(char *topic, byte *payload, unsigned int length) 
{
  String message;
  //StaticJsonDocument<256> doc; 
  Serial.print("Message received on topic: ");
  Serial.print(topic);
  Serial.println("]: ");
  for (int i = 0; i < length; i++) {
      //Serial.print((char) payload[i]);
      message += (char)payload[i];
  }
  //Serial.println(message);
  // Deserialize the JSON document
  DeserializationError error = deserializeJson(doc, message);

  // Test if parsing succeeds
  if (error) {
    Serial.print(F("deserializeJson() failed: "));
    Serial.println(error.f_str());
    return;
  }
  newPatient = doc["newPatient"];
  patientID = doc["patientID"];
  healthStatus = doc["healthStatus"].as<String>();
  waitingTime = doc["waitingTime"];

  Serial.println("******************");
  Serial.print("newPatient :");
  Serial.println(newPatient);
  Serial.print("patientID :");
  Serial.println(patientID);
  Serial.print("healthStatus :");
  Serial.println(healthStatus);
  Serial.print("waitingTime :");
  Serial.println(waitingTime);
  Serial.println("******************");
  //Serial.println();
}

void sendJSON()
{
  if (!mqtt_client.connected()) 
  {
    connectToMQTT();
  }
  mqtt_client.loop();
  doc2["patientID"] = patientID;
  doc2["currentBPM"]= currentBPM;
  doc2["currentSpO2"] = currentSpO2;
  doc2["currentTemp"] = currentTemp;
  doc2["emergencyState"] = emergencyState;
  serializeJson(doc2, JSONtoSend);
  mqtt_client.publish(mqtt_publish, JSONtoSend.c_str());
}

float getMyTemp(void)
{
  float temperatureC = 0.0;  
  Serial.println("Measuring Temperature....");
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Patient ID: ");
  lcd.print(patientID);
  startMeasurementTime = millis();
  while(millis() - startMeasurementTime < sampleTime)
  {
    lcd.setCursor(0,1);
    lcd.print("Measuring Temp.");
    sensors.requestTemperatures(); 
    temperatureC = sensors.getTempCByIndex(0);
    delay(100);
    lcd.setCursor(0,1);
    lcd.print("Measuring Temp.");
  }
  Serial.print("Temperature : ");
  Serial.print(temperatureC);
  Serial.println("  oC");
  return temperatureC;

}

void makeBeep()
{
  digitalWrite(buzzerPin, HIGH);
  delay(100);
  digitalWrite(buzzerPin, LOW);
  delay(200);
  digitalWrite(buzzerPin, HIGH);
  delay(100);
  digitalWrite(buzzerPin, LOW);
}

float getMyBPM()
{
  //Serial.println("Checking BPM");
  float valueOfBPM;
  for(int i=0; i<avgReadings; i++)
  {
    pox.update();
    valueOfBPM = valueOfBPM + pox.getHeartRate();
    delay(1);
  }
  return (valueOfBPM/avgReadings);
}

float getMySpO2()
{
  float valueOfSpO2 = 0;
  for(int i=0; i<avgReadings; i++)
  {
    pox.update();
    valueOfSpO2 = valueOfSpO2 + pox.getSpO2();
    delay(1);
  }
  return (valueOfSpO2/avgReadings);
}