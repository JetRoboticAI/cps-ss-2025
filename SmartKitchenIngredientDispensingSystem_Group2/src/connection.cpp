#include "config.h"
#include <WiFi.h>
#include <WiFiMulti.h>
#include <PubSubClient.h>
#include <Arduino.h>
#include "connection.h"
#include "dispenser.h"
#include <ArduinoJson.h>

WiFiMulti wifiMulti;
WiFiClient espClient;
PubSubClient client(espClient);

void connectToWiFi()
{
    WiFi.mode(WIFI_STA);
    wifiMulti.addAP(HOME_WIFI_SSID, HOME_WIFI_PASS);
    wifiMulti.addAP(LAB_WIFI_SSID, LAB_WIFI_PASS);

    while (wifiMulti.run() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }
    Serial.println();
    Serial.println("WiFi connected");
    Serial.println(WiFi.localIP());
}

void connectToMQTT()
{
    client.setServer(MQTT_SERVER, MQTT_PORT);
    client.setCallback(mqttCallback);
    reconnectMQTT();
}

void mqttCallback(char *topic, byte *payload, unsigned int length)
{
    JsonDocument doc;
    DeserializationError error = deserializeJson(doc, payload, length);

    if (error)
    {
        Serial.println("JSON parse error");
        publishStatus(1, "ERROR: JSON parse error");
        return;
    }

    String topicStr = String(topic);

    if (topicStr == PING_TOPIC && doc["CMD"] == "reboot")
    {
        ESP.restart();
    }

    /* CMD
    #define CMD {"flag" : 0, "pos" : {0, 0, 0, 0}, "count" : {0, 0, 0, 0}}
    flag 0 = DISPENSE, 1 = OPEN, 2 = CLOSE, 3 = CW 1 STEP, 4 = CCW 1 STEP
    pos = 0 disable 1 enable for each position in order LEFT_BOTTOM, LEFT_TOP, RIGHT_BOTTOM, RIGHT_TOP
    count = number for each position in order LEFT_BOTTOM, LEFT_TOP, RIGHT_BOTTOM, RIGHT_TOP
    */
    if (topicStr.endsWith("/open"))
    {
        try
        {
            if (!doc.containsKey("flag") || !doc.containsKey("pos") || !doc.containsKey("count"))
            {
                Serial.println("Missing required fields");
                publishStatus(1, "ERROR: Missing required fields");
                return;
            }
            if (!doc["pos"].is<JsonArray>() || !doc["count"].is<JsonArray>())
            {
                Serial.println("pos or count is not an array");
                publishStatus(1, "ERROR: pos or count is not an array");
                return;
            }
            if (doc["pos"].size() != 4 || doc["count"].size() != 4)
            {
                Serial.println("pos or count array size invalid");
                publishStatus(1, "ERROR: pos or count array size invalid");
                return;
            }
            int flag = doc["flag"] | 0;
            if (flag < 0 || flag > 4)
            {
                Serial.println("Invalid flag");
                publishStatus(1, "ERROR: Invalid flag");
                return;
            }
            bool pos[4];
            int count[4];
            for (int i = 0; i < 4; i++)
            {
                int p = doc["pos"][i] | 0;
                int c = doc["count"][i] | 0;
                if (p != 0 && p != 1)
                {
                    Serial.println("Invalid position value");
                    publishStatus(1, "ERROR: Invalid position value");
                    return;
                }
                if (c < 0)
                {
                    Serial.println("Invalid count value");
                    publishStatus(1, "ERROR: Invalid count value");
                    return;
                }
                pos[i] = p;
                count[i] = c;
            }
            Serial.println(doc.as<String>());
            if (!isBusy())
            {
                // Serial.print("Flag: ");
                // Serial.println(flag);
                // Serial.print("Pos: ");
                // for (int i = 0; i < 4; i++)
                // {
                //     Serial.print(pos[i]);
                //     Serial.print(": ");
                //     Serial.print(count[i]);
                //     Serial.print(", ");
                // }
                // Serial.println();
                queueTask(flag, pos, count);
            }
            else
            {
                Serial.println("Busy");
                publishStatus(1, "BUSY");
            }
        }
        catch (const std::exception &e)
        {
            Serial.println("Error parsing open command");
            publishStatus(1, "ERROR: Parsing error");
            return;
        }
    }
    else
    {
        Serial.print("Message arrived [");
        Serial.print(topic);
        Serial.print("]: ");
        Serial.print(doc.as<String>());
        Serial.println();
    }
}

void reconnectMQTT()
{
    if (!client.connected())
    {
        Serial.print("Attempting MQTT connection...");
        if (client.connect(DISPENSER_ID))
        {
            Serial.println("connected");
            client.subscribe(DISPENSE_TOPIC);
        }
        else
        {
            Serial.print("failed, rc=");
            Serial.print(client.state());
            Serial.println(" try again in 5 seconds");
        }
    }
}

void loopMQTT()
{
    static unsigned long lastReconnect = 0;
    unsigned long now = millis();
    if (!client.connected())
    {
        if (now - lastReconnect > RECONNECT_INTERVAL)
        {
            lastReconnect = now;
            reconnectMQTT();
        }
    }
    client.loop();
}

void publishStatus(bool att, String status)
{
    JsonDocument doc;
    doc["att"] = att;
    doc["status"] = status;

    if (client.connected())
    {
        char buffer[256];
        serializeJson(doc, buffer);
        client.publish(STATUS_TOPIC, buffer);
    }
    else
    {
        Serial.println("MQTT client not connected, cannot publish status.");
    }
}