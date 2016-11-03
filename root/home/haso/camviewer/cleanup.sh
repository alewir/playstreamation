#!/usr/bin/env bash

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

rm -rfv *.log
rm -rfv *.log.*
rm -rfv *.pyc
rm -rfv start?.sh

cp -v config_cam.cfg ../
cp -v config_mon.cfg ../
cp -v interfaces ../

rm -rfv config_cam.cfg

svn revert config_mon.cfg
svn revert interfaces
