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

ps -ef | grep "[o]mxplayer.bin" | awk '{print $2}' | xargs -n 1 sudo kill -s SIGINT

screen -X -S camera0 kill
screen -X -S camera1 kill
screen -X -S camera2 kill
screen -X -S camera3 kill

exit 0

