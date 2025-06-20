#include <Arduino.h>
#include <Stepper.h>
#include "config.h"

const int stepsPerRev = STEPS_PER_REV;
const int motorAPins[] = MOTOR_A_PINS;
const int motorBPins[] = MOTOR_B_PINS;
const int motorStepsLB = MOTOR_ANGLE_LB * stepsPerRev / 360;
const int motorStepsLT = MOTOR_ANGLE_LT * stepsPerRev / 360;
const int motorStepsRB = MOTOR_ANGLE_RB * stepsPerRev / 360;
const int motorStepsRT = MOTOR_ANGLE_RT * stepsPerRev / 360;

Stepper MotorA(stepsPerRev, motorAPins[0], motorAPins[1], motorAPins[2], motorAPins[3]);
Stepper MotorB(stepsPerRev, motorBPins[0], motorBPins[1], motorBPins[2], motorBPins[3]);

void initStepperMotor()
{
    MotorA.setSpeed(15);
    MotorB.setSpeed(15);
}

void openOne(Position pos)
{
    switch (pos)
    {
    case LEFT_BOTTOM:
        MotorA.step(motorStepsLB);
        break;
    case LEFT_TOP:
        MotorA.step(-motorStepsLT);
        break;
    case RIGHT_BOTTOM:
        MotorB.step(-motorStepsRB);
        break;
    case RIGHT_TOP:
        MotorB.step(motorStepsRT);
        break;
    default:
        break;
    }
}

void closeOne(Position pos)
{
    switch (pos)
    {
    case LEFT_BOTTOM:
        MotorA.step(-motorStepsLB);
        break;
    case LEFT_TOP:
        MotorA.step(motorStepsLT);
        break;
    case RIGHT_BOTTOM:
        MotorB.step(motorStepsRB);
        break;
    case RIGHT_TOP:
        MotorB.step(-motorStepsRT);
        break;
    default:
        break;
    }
}

void stepOne(Position pos, int steps)
{
    switch (pos)
    {
    case LEFT_BOTTOM:
        MotorA.step(steps);
        break;
    case LEFT_TOP:
        MotorA.step(-steps);
        break;
    case RIGHT_BOTTOM:
        MotorB.step(-steps);
        break;
    case RIGHT_TOP:
        MotorB.step(steps);
        break;
    default:
        break;
    }
}


void resetMotorPin()
{
    for (int i = 0; i < 4; i++)
    {
        digitalWrite(motorAPins[i], LOW);
        digitalWrite(motorBPins[i], LOW);
    }
}

// void dropOne(Position pos)
// /*
// two stepper motors
// Motor 1 Left:
// When a command is received, the motor always rotates to either direction (depends on the ingredient) for a certain speed and angle,
// then goes back to the initial position same speed.
// Motor 2 Right
// */
// {
//     openOne(pos);
//     delay(300);
//     closeOne(pos);
//     delay(100);
//     resetMotorPin();
// }