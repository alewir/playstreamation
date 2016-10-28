#!/usr/bin/env bash

ps -ef | grep "[o]mxplayer.bin" | awk '{print $2}' | xargs -n 1 sudo kill -s SIGINT

screen -X -S camera0 kill
screen -X -S camera1 kill
screen -X -S camera2 kill
screen -X -S camera3 kill

exit 0
