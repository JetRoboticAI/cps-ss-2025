#include <WiFi.h>            // For connecting ESP32 to Wi-Fi network
#include <HTTPClient.h>      // For sending HTTP POST requests
#include <HX711.h>           // For reading data from the load cell amplifier
#include <TFT_eSPI.h>        // For controlling the TFT LCD
#include <SPI.h>             // SPI library used by TFT display

// Pin definitions
#define HX711_DOUT 32        // Data pin from HX711 to ESP32
#define HX711_SCK 33         // Clock pin from ESP32 to HX711
#define LCD_BACKLIGHT_PIN 21 // Controls the LCD backlight
#define TARE_BUTTON_PIN 5    // GPIO connected to the capacitive tare button (TTP223)

HX711 scale;                 // HX711 object for reading the load cell
TFT_eSPI tft = TFT_eSPI();   // TFT LCD object

// Wi-Fi network and server settings
const char* ssid = "";    // Wi-Fi SSID
const char* password = ""; // Wi-Fi password
const char* serverURL = "http://192.168.66.237:5000/api/push_weight"; // Flask server endpoint

float calibration_factor = 1.0;  // Calibration factor to convert raw ADC values to grams
bool lastButtonState = LOW;     // Last known state of the tare button
const float KNOWN_WEIGHT_GRAMS = 100.0; // Known calibration weight for initial scaling

void setup() {
  Serial.begin(9600);  // Initialize serial monitor
  delay(500);

  // Initialize and clear TFT display
  tft.init();
  tft.setRotation(4);
  tft.fillScreen(TFT_WHITE);
  tft.setTextColor(TFT_BLACK, TFT_WHITE);
  tft.setTextSize(2);
  tft.setCursor(10, 40);
  tft.println("Smart IoT Scale");

  // Initialize HX711 and check connection
  scale.begin(HX711_DOUT, HX711_SCK);
  if (!scale.is_ready()) {
    Serial.println("HX711 not connected. Check wiring.");
    tft.setCursor(10, 80);
    tft.println("HX711 ERROR");
    while (true);  // Halt if HX711 not detected
  }

  // Perform tare to zero the scale
  Serial.println("Taring... make sure scale is empty.");
  tft.setCursor(10, 80);
  tft.println("Taring...");
  delay(2000);
  scale.tare();
  tft.fillRect(0, 80, 240, 30, TFT_WHITE);

  // Wait for user to place 100g weight for calibration
  Serial.println("Place a 100g weight for calibration.");
  tft.setCursor(10, 80);
  tft.println("Place 100g...");
  delay(5000);  // Wait for placement

  // Calculate scale factor based on known weight
  long reading = scale.get_value(20);
  calibration_factor = static_cast<float>(reading) / KNOWN_WEIGHT_GRAMS;
  scale.set_scale(calibration_factor);

  Serial.print("Calibration factor: ");
  Serial.println(calibration_factor, 4);
  tft.fillRect(0, 80, 240, 30, TFT_WHITE);
  tft.setCursor(10, 80);
  tft.print("Calib = ");
  tft.println(calibration_factor, 1);
  delay(2000);
  tft.fillScreen(TFT_WHITE);

  // Turn on LCD backlight
  pinMode(LCD_BACKLIGHT_PIN, OUTPUT);
  digitalWrite(LCD_BACKLIGHT_PIN, HIGH);

  // Set tare button pin as input
  pinMode(TARE_BUTTON_PIN, INPUT);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("Wi-Fi connected, IP: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // Read current weight value and raw sensor data
  float weight = scale.get_units(5);  // Average of 5 readings
  long raw = scale.get_value();
  long offset = scale.get_offset();

  // Check if tare button is pressed (rising edge)
  bool buttonState = digitalRead(TARE_BUTTON_PIN);
  if (buttonState == HIGH && lastButtonState == LOW) {
    Serial.println("Tare button pressed.");
    tft.fillScreen(TFT_WHITE);
    tft.setCursor(10, 100);
    tft.setTextSize(2);
    tft.println("Taring...");
    delay(300);
    scale.power_down();  // Temporarily power down to reset
    delay(100);
    scale.power_up();
    delay(500);
    scale.tare();        // Re-zero the scale
    Serial.println("Tare complete.");
    delay(800);
    tft.fillRect(10, 100, 240, 50, TFT_WHITE);  // Clear display
  }
  lastButtonState = buttonState;

  // Update TFT display with current reading
  tft.fillRect(0, 130, 240, 60, TFT_WHITE);  // Clear previous display
  tft.setCursor(10, 140);
  tft.setTextSize(2);
  tft.println("Smart Food Scale");
  tft.setCursor(10, 170);
  tft.print("Mass: ");
  tft.print(weight, 1);
  tft.println(" g");

  // Print debugging info to serial monitor
  Serial.print("Raw: ");
  Serial.print(raw);
  Serial.print(" | Weight: ");
  Serial.print(weight, 2);
  Serial.print(" g | Offset: ");
  Serial.print(offset);
  Serial.print(" | Scale: ");
  Serial.println(calibration_factor, 4);

  // Send weight to Flask server via HTTP POST
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverURL);
    http.addHeader("Content-Type", "application/json");

    String payload = "{\"weight\": " + String(weight, 2) + "}";
    int httpResponseCode = http.POST(payload);

    if (httpResponseCode > 0) {
      Serial.println("POST Success: " + String(httpResponseCode));
    } else {
      Serial.println("POST Failed: " + http.errorToString(httpResponseCode));
    }

    http.end();
  } else {
    Serial.println("Wi-Fi disconnected.");
  }

  delay(1000);  // Wait 1 second before next reading
}
