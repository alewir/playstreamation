#!/usr/bin/env bash

sudo ln -s /home/haso/camviewer/branding/splash.jpg /etc/splash.jpg
sudo ln -s /home/haso/camviewer/asplashscreen /etc/init.d/asplashscreen

sudo chmod a+x /etc/init.d/asplashscreen
sudo insserv /etc/init.d/asplashscreen
