#include <wiringPi.h>
#include <softPwm.h>
#include <stdio.h>
#include <stdlib.h>
#include "DHT.hpp" 

// RGB LED softPWM 
#define LED_R 22
#define LED_G 23
#define LED_B 24

// DHT11 
#define DHT_PIN 0


#define RELAY_PIN 4


#define HUMIDITY_THRESHOLD 40.0
#define TEMP_LOW 20.0
#define TEMP_HIGH 28.0

void setupLed() {
    softPwmCreate(LED_R, 0, 100);
    softPwmCreate(LED_G, 0, 100);
    softPwmCreate(LED_B, 0, 100);
}

void setColor(int r, int g, int b) {
    softPwmWrite(LED_R, r);
    softPwmWrite(LED_G, g);
    softPwmWrite(LED_B, b);
}

int main() {
    DHT dht;
    int chk;
    
    wiringPiSetup();
    setupLed();
    pinMode(RELAY_PIN, OUTPUT);
    digitalWrite(RELAY_PIN, HIGH);  

    while (1) {
        chk = dht.readDHT11(DHT_PIN);
        if (chk == DHTLIB_OK) {
            float temp = dht.temperature;
            float humi = dht.humidity;
            printf("Temp = %.1f°C, Humidity = %.1f%%\n", temp, humi);
            //test code
            //float temp = 15 + rand() % 20;
            //float humi = 30 + rand() % 40;
            //printf("Temp = %.1f celsius, Humidity = %.1f%%\n", temp,humi);
        
            // LED 
            if (temp > TEMP_HIGH) {
                setColor(100, 0, 0);   // red
            } else if (temp < TEMP_LOW) {
                setColor(0, 0, 100);   // blue
            } else {
                setColor(50, 0, 50);   // purple
            }

            // water pump
            if (humi < HUMIDITY_THRESHOLD) {
                printf("湿度 %.1f%% 过低，启动水泵\n", humi);
                digitalWrite(RELAY_PIN, LOW);   // open water pump
                delay(3000);                    // run 3 seconds 
                digitalWrite(RELAY_PIN, HIGH);  // close water pump
            } else {
                printf("temp nomal, no need to open water pump\n");
            }
        } 
       else {
            printf("read DHT11 failed，code: %d\n", chk);
        }

        delay(5000);  // check every 5 seconds
     }

    return 0;
}
