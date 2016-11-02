#!/usr/bin/env python
# coding=utf-8

# Copyright (C) 2016. Haso S.C. J. Macioszek & A. Paszek
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

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
