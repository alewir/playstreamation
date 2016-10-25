#!/usr/bin/env bash

win_coords=$1

if [ -n "$win_coords" ]; then
    ps_count=`ps -ef | grep "[o]mxplayer.bin" | grep "$win_coords" | awk '{print $2}' | wc -l`
    echo ${ps_count}
else
    echo -1
fi
