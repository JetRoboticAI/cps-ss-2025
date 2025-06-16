#include <DHT.h>

#define DHTPIN 2
#define DHTTYPE DHT11

const int ledPin = 6;
const int airPin = A1;
const int sampleCount = 15;

float tempSamples[sampleCount];
float humiSamples[sampleCount];

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  dht.begin();
  pinMode(ledPin, OUTPUT);
}

void loop() {
  for (int i = 0; i < sampleCount; i++) {
    float t = dht.readTemperature();
    float h = dht.readHumidity();

    if (isnan(t) || isnan(h)) {
      Serial.println("Failed to read from DHT11 sensor!");
      return;
    }

    tempSamples[i] = t;
    humiSamples[i] = h;
    delay(200);
  }

  float tempSum = 0, tempMax = tempSamples[0], tempMin = tempSamples[0];
  for (int i = 0; i < sampleCount; i++) {
    if (tempSamples[i] > tempMax) tempMax = tempSamples[i];
    if (tempSamples[i] < tempMin) tempMin = tempSamples[i];
    tempSum += tempSamples[i];
  }
  float avgTemp = (tempSum - tempMax - tempMin) / (sampleCount - 2);

  float humiSum = 0, humiMax = humiSamples[0], humiMin = humiSamples[0];
  for (int i = 0; i < sampleCount; i++) {
    if (humiSamples[i] > humiMax) humiMax = humiSamples[i];
    if (humiSamples[i] < humiMin) humiMin = humiSamples[i];
    humiSum += humiSamples[i];
  }
  float avgHumi = (humiSum - humiMax - humiMin) / (sampleCount - 2);

  int airValue = analogRead(airPin);

  Serial.println(F("================== In-Vechile Environment Report =================="));
  Serial.print(F("Avg Temperature: "));
  Serial.print(avgTemp, 1);
  Serial.println(" °C");

  Serial.print(F("Avg Humidity   : "));
  Serial.print(avgHumi, 1);
  Serial.println(" %");

  Serial.print(F("Air Quality    : "));
  Serial.print(airValue);
  if (airValue >= 400) Serial.println("Poor");
  else if (airValue >= 250) Serial.println("Moderate");
  else Serial.println("Good");

  Serial.println(F("=========================================================="));
  Serial.println();

  if (avgTemp >= 29.0 || airValue > 400) {
    digitalWrite(ledPin, HIGH);
  } else {
    digitalWrite(ledPin, LOW);
  }
}
