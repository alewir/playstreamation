#!/usr/bin/env bash

ps -ef | grep "[o]mxplayer.bin" | grep "528" | awk '{print $2}' | xargs -n 1 sudo kill -s SIGINT

