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
