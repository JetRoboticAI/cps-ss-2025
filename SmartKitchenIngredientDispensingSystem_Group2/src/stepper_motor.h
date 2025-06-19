#ifndef STEPPER_MOTOR_H
#define STEPPER_MOTOR_H
#include "config.h"


void initStepperMotor();
void openOne(Position pos);
void closeOne(Position pos);
void stepOne(Position pos, int steps);
void resetMotorPin();

#endif