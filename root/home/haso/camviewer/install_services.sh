#!/usr/bin/env bash

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

