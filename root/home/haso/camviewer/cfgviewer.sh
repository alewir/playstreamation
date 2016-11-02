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

export PS_HOME=/home/haso/camviewer

cd "$PS_HOME"/cfgviewer

IP_ADDRESS=`awk '$1=="address" {print $2}' "$PS_HOME"/config_mon.cfg`
MON_URL="$IP_ADDRESS":8080

python manage.py migrate
python manage.py runserver --insecure "$MON_URL" > "$PS_HOME"/cfgviewer.log 2>&1

cd -

exit 0
