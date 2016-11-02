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

export INSTALL_DIR=~haso/camviewer

sudo mkdir /etc/service

export INSTALL_DIR=~haso/camviewer

sudo bash remove_services.sh

SERVICES=(camviewer cfgviewer watchdog buttons)
for SCRIPT in ${SERVICES[*]}
do
    echo "Setting up $SCRIPT"
    chmod 755 "$INSTALL_DIR"/service/$SCRIPT/run
    sudo cp -rfv "$INSTALL_DIR"/service/$SCRIPT /service/
    echo " -- Linking..."
    sudo ln -vsT /service/$SCRIPT /etc/service/service-$SCRIPT
done

echo "Results:"
sudo tree /service
sudo tree /etc/service

exit 0

