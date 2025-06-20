#include <Arduino.h>
#include "connection.h"
#include "dispenser.h"
#include "IR_sensor.h"

static bool isReported = false;
static unsigned long lastReportTime = 0;
static unsigned long lastStatusTime = 0;
static unsigned long lastMQTTTime = 0;
static unsigned long lastDispenseTime = 0;

void reportHolder()
{
    if (!isAvailable() && !isReported)
    {
        Serial.println("Holder unavailable");
        publishStatus(1, "BLOCKED");
        isReported = true;
    }
    if (isAvailable() && !isBusy())
    {
        Serial.println("Holder available");
        publishStatus(0, "READY");
        isReported = false;
    }
}

void setup()
{
    Serial.begin(115200);
    connectToWiFi();
    connectToMQTT();
    initDispenser();
    publishStatus(0, "INIT");
}

void loop()
{
    unsigned long now = millis();

    if (now - lastMQTTTime > MQTT_INTERVAL)
    {
        lastMQTTTime = now;
        loopMQTT();
    }

    if (now - lastStatusTime > STATUS_INTERVAL)
    {
        lastStatusTime = now;
        updateHolder();
    }

    if (now - lastReportTime > REPORT_INTERVAL)
    {
        lastReportTime = now;
        reportHolder();
    }

    if (isAvailable() && isBusy())
    {
        if (now - lastDispenseTime > DISPENSE_INTERVAL)
        {
            loopDispenser();
            lastDispenseTime = now;
        }
    }
}
