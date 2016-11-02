#!/usr/bin/env bash

sudo apt-get update

sudo apt-get install python-dev python-pip
sudo apt-get install subversion
sudo apt-get install daemontools daemontools-run
sudo apt-get install python-imaging-tk
sudo apt-get install screen
sudo apt-get install fbi

# tested with version: 1.9.4
sudo pip install django
# tested with version: 0.0.4
sudo pip install pyping
# tested with version: 2.1.2
sudo pip install fysom
# tested with version: 15.2.0
sudo pip install pyzmq

export PS_USER=haso
export REPO_URL=https://github.com/alewir/playstreamation.git/trunk/

cd /home/"$PS_USER"
mkdir camviewer
sudo chown "$PS_USER" camviewer
cd camviewer
export PS_HOME=`pwd`  # TODO: this path needs to be stored and set at startup (preferably for all users)

svn co "REPO_URL" .
sudo chown -R "$PS_USER" *

bash fix_permissions.sh
./install_services.sh
./install_logo.sh

sudo mv -vf /etc/network/interfaces /etc/network/interfaces.old
sudo ln -vs "$PS_HOME"/interfaces /etc/network/interfaces

sudo mv -vf /etc/splash.jpg /etc/splash.jpg.old
sudo ln -vs "$PS_HOME"/branding/splash.jpg /etc/splash.jpg

exit 0
