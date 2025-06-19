#ifndef CONNECTION_H
#define CONNECTION_H
#include <Arduino.h>

void connectToWiFi();
void connectToMQTT();
void publishStatus(bool att, String status);
void mqttCallback(char *topic, byte *payload, unsigned int length);
void reconnectMQTT();
void loopMQTT();
#endif