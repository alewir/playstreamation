#!/usr/bin/env bash

# using version: 1.9.4
sudo pip install django
# using version: 0.0.4
sudo pip install pyping

sudo apt-get update
sudo apt-get install subversion

export PS_USER=haso
export REPO_URL=svn co https://github.com/alewir/playstreamation.git/trunk/ .

cd /home/"$PS_USER"
mkdir camviewer
sudo chown "$PS_USER" camviewer
cd camviewer
export PS_HOME=`pwd`  # TODO: this path needs to be stored and set at startup (preferably for all users)

svn co "REPO_URL" .
sudo chown -R "$PS_USER" *

bash fix_permissions.sh
./install_services.sh

sudo mv -vf /etc/network/interfaces /etc/network/interfaces.old
sudo ln -vs "$PS_HOME"/interfaces /etc/network/interfaces

sudo mv -vf /etc/splash.jpg /etc/splash.jpg.old
sudo ln -vs "$PS_HOME"/branding/splash.jpg /etc/splash.jpg

exit 0