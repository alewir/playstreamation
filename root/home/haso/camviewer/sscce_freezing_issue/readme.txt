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

# prerequisites:
sudo apt-get update && sudo apt-get upgrade
sudo apt-get install screen
sudo apt-get install subversion

# SSCCE installation
mkdir playstreamation_issue
cd playstreamation_issue
svn co https://github.com/alewir/playstreamation.git/trunk/root/home/haso/camviewer/sscce_freezing_issue/ .
chmod 755 *.sh

# Raspbian preparation 
#
# Apply settings from
#   https://github.com/alewir/playstreamation/wiki/OS-preparation
# OS preparation sections that are mandatory to apply:
#   Initial OS setup after installation
#     Update permissions for omxplayer process executed by a user ('haso' user is used as example)
#   Screen & Video
#     Basic video configuration
#     Disabling screen saver

sudo reboot

# start with:
./start.sh
