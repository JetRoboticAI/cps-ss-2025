#ifndef CONFIG_H
#define CONFIG_H

#define HOME_WIFI_SSID "COGECO-222E58"
#define HOME_WIFI_PASS "uw5mmnkj"

#define LAB_WIFI_SSID "SEPT SmartLAB 537"
#define LAB_WIFI_PASS "Factory1"

#define SUSHANT_SSID "BELL485"
#define SUSHANT_PASS "6695F65FC5A6"

#define MQTT_SERVER "broker.hivemq.com"
#define MQTT_PORT 1883

#define DISPENSER_ID "dispenser_A"
#define DISPENSE_TOPIC "dispenser/test/esp32/#"
#define STATUS_TOPIC "dispenser/status/esp32/A"
#define PING_TOPIC "dispenser/test/esp32/ping"

#define STEPS_PER_REV 2048
#define MOTOR_A_PINS {19, 17, 18, 16}
// #define MOTOR_A_PINS {16, 18, 17, 19}
#define MOTOR_B_PINS {13, 26, 25, 27}
// define MOTOR_B_PINS {27, 25, 26, 13}
// #define SENSOR_PIN_EN 39
#define SENSOR_PIN_OUT 34

#define RECONNECT_INTERVAL 5000
#define MOTOR_INTERVAL 300
#define RESET_INTERVAL 300
#define DISPENSE_INTERVAL 100
#define REPORT_INTERVAL 1000
#define STATUS_INTERVAL 50
#define MQTT_INTERVAL 20

enum Position
{
    LEFT_BOTTOM,
    LEFT_TOP,
    RIGHT_BOTTOM,
    RIGHT_TOP,
};

#define MOTOR_ANGLE_LB 42.5 // 0 LT
#define MOTOR_ANGLE_LT 42.5 // 1 LB
#define MOTOR_ANGLE_RB 42.5 // 2 RT
#define MOTOR_ANGLE_RT 42.5 // 3 RB
#define CMD {"flag" : 0, "pos" : {0, 0, 0, 0}, "count" : {0, 0, 0, 0}}
/* flag 0 = DISPENSE, 1 = OPEN, 2 = CLOSE, 3 = CW 1 STEP, 4 = CCW 1 STEP*/

#define ORDER {"ID" : 0, "items" : [ "a", "b", "c", "d" ], "time" : "2025-01-01 00:00:00.0"}

#endif