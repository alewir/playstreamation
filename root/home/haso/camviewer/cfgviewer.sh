#!/usr/bin/env bash

export PS_HOME=/home/haso/camviewer

cd "$PS_HOME"/cfgviewer

IP_ADDRESS=`awk '$1=="address" {print $2}' "$PS_HOME"/config_mon.cfg`
MON_URL="$IP_ADDRESS":8080

python manage.py migrate
python manage.py runserver --insecure "$MON_URL" > "$PS_HOME"/cfgviewer.log 2>&1

cd -

exit 0
