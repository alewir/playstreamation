#!/usr/bin/env bash

sudo vcdbg reloc

screen -dmS camera1 sh -c 'while true; do omxplayer --adev hdmi --timeout 5 --blank --live --aspect-mode fill --avdict rtsp_transport:tcp --win 0,0,528,298 "rtsp://172.16.1.195:554/av0_1"; done'
screen -dmS camera2 sh -c 'while true; do omxplayer --adev hdmi --timeout 5 --blank --live --aspect-mode fill --avdict rtsp_transport:tcp --win 532,0,1060,298 "rtsp://172.16.1.195:554/av0_1"; done'
screen -dmS camera3 sh -c 'while true; do omxplayer --adev hdmi --timeout 5 --blank --live --aspect-mode fill --avdict rtsp_transport:tcp --win 0,302,528,600 "rtsp://172.16.1.195:554/av0_1"; done'
screen -dmS camera4 sh -c 'while true; do omxplayer --adev hdmi --timeout 5 --blank --live --aspect-mode fill --avdict rtsp_transport:tcp --win 532,302,1060,600 "rtsp://172.16.1.195:554/av0_1"; done'

while true; do sleep 10; ./testkill.sh; done
