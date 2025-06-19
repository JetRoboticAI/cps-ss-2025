#include <Arduino.h>
#include <ArduinoJson.h>
#include <algorithm>
#include "config.h"
#include "connection.h"
#include "stepper_motor.h"
#include "IR_sensor.h"
#include "dispenser.h"

/* CMD
#define CMD {"flag" : 0, "pos" : [0, 0, 0, 0], "count" : [0, 0, 0, 0]}
flag 0 = DISPENSE, 1 = OPEN, 2 = CLOSE, 3 = OPEN 1 STEP, 4 = CLOSE 1 STEP
pos = 0 disable 1 enable for each position in order LEFT_BOTTOM, LEFT_TOP, RIGHT_BOTTOM, RIGHT_TOP
count = number for each position in order LEFT_BOTTOM, LEFT_TOP, RIGHT_BOTTOM, RIGHT_TOP
*/
struct Task
{
    int flag;
    bool pos[4];
    int count[4];
    int total;
};

static Task currentTask;
static bool hasTask = false;
static int currentIndex = 0;
static int dispensed = 0;

void initDispenser()
{
    initStepperMotor();
    initIR();
    hasTask = false;
}

bool isBusy()
{
    return hasTask;
}

void queueTask(int flag, bool pos[], int count[])
{
    currentTask.flag = flag;
    for (int i = 0; i < 4; i++)
    {
        currentTask.pos[i] = pos[i];
        currentTask.count[i] = count[i];
    }
    currentTask.total = count[0] + count[1] + count[2] + count[3];
    hasTask = true;
    publishStatus(1, "RUNNING");
}

void motorBehaviour(int flag, Position pos)
{
    // Serial.print("motorBehaviour");
    Serial.println(flag, pos);
    switch (flag)
    {
    case 0:
        /* code */
        openOne(pos);
        delay(MOTOR_INTERVAL);
        closeOne(pos);
        break;
    case 1:
        openOne(pos);
        break;
    case 2:
        closeOne(pos);
        break;
    case 3:
        stepOne(pos, 1);
        break;
    case 4:
        stepOne(pos, 1);
        break;
    default:
        break;
    }
}

void loopDispenser()
{
    // Serial.print("currentIndex");
    // Serial.println(currentIndex);
    while (currentIndex < 4)
    {
        Serial.print("pos");
        Serial.println(currentTask.pos[currentIndex]);
        if (currentTask.pos[currentIndex])
        {
            if (dispensed < currentTask.count[currentIndex])
            {
                motorBehaviour(currentTask.flag, static_cast<Position>(currentIndex));
                delay(RESET_INTERVAL);
                resetMotorPin();
                dispensed++;
                break; // Exit to stay non-blocking; continue next time
            }
            else
            {
                // Finished dispensing this position
                currentTask.pos[currentIndex] = false;
                dispensed = 0;
                currentIndex++;
            }
        }
        else
        {
            // Serial.println("nextIndex");
            currentIndex++;
        }
    }
    if (currentIndex >= 4)
    {
        currentTask.flag = -1;
        currentIndex = 0;
        dispensed = 0;
        hasTask = false;
        afterDrop();
        publishStatus(1, "DONE");
    }
}