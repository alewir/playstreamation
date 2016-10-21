#!/usr/bin/env bash

sleep 5  # time for all players to initialize

proc_check=$(ps -ef | grep '[o]mxplayer.bin')
if [[ $? != 0 ]]; then
  echo "Proc check failed!"
elif [ -n "$proc_check" ]; then
  echo "Running..."
  while [ "$(ps -ef | grep '[o]mxplayer.bin' | wc -l)" -gt 0 ]; do
    sleep 1
  done
  echo "No players detected."
else
  echo "Not running."
fi

