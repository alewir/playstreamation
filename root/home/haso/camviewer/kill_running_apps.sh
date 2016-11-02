#!/usr/bin/env bash

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

PID=`ps -ef | grep "python [b]uttons.py" | awk '{print $2}'`
if [ -n "$PID" ] ; then
    echo "Closing GPIO-Buttons driver..."
    echo "$PID" | xargs -n 1 sudo kill -TERM
else
    echo "GPIO-Buttons driver not running."
fi

PID=`ps -ef | grep "python [m]anage.py runserver" | awk '{print $2}'`
if [ -n "$PID" ] ; then
    echo "Closing CFGviewer..."
    echo "$PID" | xargs -n 1 sudo kill -TERM
else
    echo "CFGviewer not running."
fi

PID=`ps -ef | grep "[c]amviewer.py" | awk '{print $2}'`
if [ -n "$PID" ] ; then
    echo "Closing CAMviewer..."
    echo "$PID" | xargs -n 1 sudo kill -TERM
else
    echo "CAMviewer not running."
fi

PID=`ps -ef | grep "[o]mxplayer.bin" | awk '{print $2}'`
if [ -n "$PID" ] ; then
    echo "Closing OMXplayer..."
    sudo python dbus_omxplayer.py
else
    echo "OMXplayer not running."
fi

./omx_kill_all.sh

# NOTE: watchdog.py process <= should not be killed (WDT will fire)
