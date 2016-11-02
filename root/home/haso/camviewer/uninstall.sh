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

bash stop.sh

export INSTALL_DIR=~haso/camviewer

sudo bash remove_services.sh

sudo rm -rvf /etc/network/interfaces
sudo mv -vf /etc/network/interfaces.old /etc/network/interfaces

sudo insserv -r /etc/init.d/asplashscreen
sudo rm -rvf /etc/init.d/asplashscreen

sudo rm -rvf /etc/splash.jpg
sudo mv -vf /etc/splash.jpg.old /etc/splash.jpg

sudo pip uninstall django
sudo pip uninstall pyping

cd $INSTALL_DIR/..
sudo rm -rvf $INSTALL_DIR

exit 0