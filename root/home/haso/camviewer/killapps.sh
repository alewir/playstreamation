#!/usr/bin/env bash

PID=`ps -ef | grep "[o]mxplayer.bin" | awk '{print $2}'`
if [ -n "$PID" ] ; then
    echo "Closing OMXplayer..."
    sudo python dbus_omxplayer.py
else
    echo "OMXplayer not running."
fi

source stop4.sh

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

# NOTE: watchdog.py process <= should not be killed (WDT will fire)
