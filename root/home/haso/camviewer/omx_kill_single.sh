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

win_coords=$1
screen_name=$2

echo 'coords='${win_coords}
echo 'screen='${screen_name}

if [ -n "$win_coords" ] && [ -n "$screen_name" ]; then
    echo "Killing all processes for ($screen_name) and ($win_coords)..."
    ps_list=`ps -ef | grep "[o]mxplayer.bin" | grep "$win_coords"`
    echo "ps results="${ps_list}
    pid_s=`echo "$ps_list" | awk '{print $2}'`
    echo "PIDS="${pid_s}
    echo "$pid_s" | xargs -n 1 sudo kill -s SIGKILL
    screen -X -S "$screen_name" kill
    exit 0
else
    echo "No parameter given."
    exit 1
fi
