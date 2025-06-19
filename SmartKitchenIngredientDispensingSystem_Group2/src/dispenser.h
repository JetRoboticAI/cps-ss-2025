#ifndef DISPENSER_H
#define DISPENSER_H
#include "config.h"

void initDispenser();
void loopDispenser();
bool isBusy();
void queueTask(int flag, bool pos[], int count[]);

#endif