# prerequisites:
sudo apt-get update && sudo apt-get upgrade
sudo apt-get install screen
sudo apt-get install subversion

# SSCCE installation
mkdir playstreamation_issue
cd playstreamation_issue
svn co https://github.com/alewir/playstreamation.git/trunk/root/home/haso/camviewer/sscce_freezing_issue/ .
chmod 755 *.sh

# start with:
./start.sh
