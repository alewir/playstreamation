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

SERVICES=(camviewer cfgviewer watchdog buttons)

for SCRIPT in ${SERVICES[*]}
do
    echo "Cleaning up $SCRIPT"
    sudo rm -rvf /etc/service/service-$SCRIPT
    sudo rm -rvf /service/$SCRIPT
done

echo "Results:"
sudo tree /service
sudo tree /etc/service

exit 0

