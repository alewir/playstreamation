#!/usr/bin/env bash

echo "Stopping services..."
sudo svc -d /service/buttons/
sudo svc -d /service/camviewer/
sudo svc -d /service/cfgviewer/

echo "Killing apps..."
sleep 3

source ./killapps.sh


