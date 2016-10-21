#!/usr/bin/env bash

rm -rf *.log
rm -rf *.log.*
rm -rf *.pyc

rm -rf config_cam.cfg

svn revert config_mon.cfg
