#!/usr/bin/env python
# coding=utf-8

import time

import RPi.GPIO as GPIO

WDT_PIN_STROBE = 21
WDT_PIN_REN = 16

GPIO.setmode(GPIO.BCM)

GPIO.setup(WDT_PIN_STROBE, GPIO.OUT)
GPIO.setup(WDT_PIN_REN, GPIO.OUT)

GPIO.output(WDT_PIN_REN, True)


def strobe():
    GPIO.output(WDT_PIN_STROBE, False)
    time.sleep(0.1)

    GPIO.output(WDT_PIN_STROBE, True)
    time.sleep(0.1)


initializing = 1
while True:
    for x in range(0, 10):  # for ~2 second(s)...
        strobe()

    if initializing == 1:
        # and then: Reset Enabled
        GPIO.output(WDT_PIN_REN, False)
        initializing = 0  # once
