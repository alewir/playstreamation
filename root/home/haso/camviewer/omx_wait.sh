#!/usr/bin/env bash

sleep 5  # time for all players to initialize

proc_check=$(ps -ef | grep '[o]mxplayer.bin')
if [[ $? != 0 ]]; then
    echo "Proc check failed!"
    exit 1
elif [ -n "$proc_check" ]; then
    echo "Running..."
    while [ "$(ps -ef | grep '[o]mxplayer.bin' | wc -l)" -gt 0 ]; do
        sleep 1
    done

    echo "All players stopped."
    exit 0
else
    echo "No players were running."
    exit 0
fi
