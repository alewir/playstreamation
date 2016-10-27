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
