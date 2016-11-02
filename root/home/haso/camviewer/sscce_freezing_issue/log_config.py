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

import logging

from logging.handlers import RotatingFileHandler

# create & configure logger
log_level = logging.INFO

log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

log_handler_file = RotatingFileHandler(filename='player4cams.log', mode='w', maxBytes=10000000, backupCount=3)
log_handler_console = logging.StreamHandler()
log_handler_console.setLevel(log_level)
log_handler_console.setFormatter(log_formatter)

log = logging.getLogger('player4cams')
log.setLevel(log_level)
log_handler_file.setLevel(log_level)
log_handler_file.setFormatter(log_formatter)
log.addHandler(log_handler_console)
log.addHandler(log_handler_file)
