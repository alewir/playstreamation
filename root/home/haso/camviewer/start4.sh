#!/usr/bin/env bash
screen -dmS camera1 sh -c 'omxplayer --adev hdmi --timeout 5 --blank --live --aspect-mode fill --win 0,0,528,298 "rtsp://172.16.1.195:554/av0_1&user=admin&password=admin"'
screen -dmS camera2 sh -c 'omxplayer --adev hdmi --timeout 5 --blank --live --aspect-mode fill --win 532,0,1060,298 "rtsp://172.16.1.191:554/av0_1&user=admin&password=admin"'
screen -dmS camera3 sh -c 'omxplayer --adev hdmi --timeout 5 --blank --live --aspect-mode fill --win 0,302,528,600 "rtsp://172.16.1.192:554/av0_1"'
screen -dmS camera4 sh -c 'omxplayer --adev hdmi --timeout 5 --blank --live --aspect-mode fill --win 532,302,1060,600 "rtsp://172.16.1.202:554/av0_1"'
/home/haso/camviewer/wait_for_omx.sh
