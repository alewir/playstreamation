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

if [ -n "$win_coords" ]; then
    ps_count=`ps -ef | grep "[o]mxplayer.bin" | grep "$win_coords" | awk '{print $2}' | wc -l`
    echo ${ps_count}
else
    echo -1
fi
