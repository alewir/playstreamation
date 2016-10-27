#!/usr/bin/env bash

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