#!/usr/bin/env bash

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

