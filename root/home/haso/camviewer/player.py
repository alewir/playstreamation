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
import os
from subprocess import Popen, PIPE, STDOUT

from log_config import log

KEY_OMXPLAYER_QUIT = 'q'

PLAYER_NAME = 'omxplayer'
logger = logging.getLogger(__name__)
DEV_NULL = open(os.devnull, 'w')


class Player:
    def __init__(self, ident, uri, win, live=True):
        self.id = ident
        self.live = live
        self.uri = uri
        self.win = win
        self.process = None

    def play(self):
        self._stop()

        # e.g. (no auth): omxplayer -o hdmi --blank --live --fps 24 -r rtsp://172.16.1.195
        # e.g. (auth)   : sudo omxplayer -o hdmi --blank --live "rtsp://172.16.1.195/av0_0&user=admin&password=admin"

        command = ['omxplayer',
                   '--adev', 'hdmi',
                   '--aidx', "-1",  # disable audio
                   '--timeout', '5',
                   '--blank',
                   '--live' if self.live else '--no-osd',
                   '--aspect-mode', 'fill',
                   '--avdict', 'rtsp_transport:tcp',
                   '--subtitles', '/home/haso/camviewer/sub%d.srt' % self.id,
                   self.uri]
        log.info('Starting Player[single]... (%s)' % repr(command))
        self.process = Popen(command, stdin=PIPE, stdout=DEV_NULL, stderr=STDOUT, close_fds=True, bufsize=0)  # async. execution, instant exit
        log.info('Player[single] started.')

    def wait_to_finish(self):
        log.info('Waiting for player[single] process to stop.')
        self.process.wait()
        self.process = None
        log.info('Player[single] process stopped.')

    def _stop(self):
        if self.process is not None:
            try:
                self.process.stdin.write(KEY_OMXPLAYER_QUIT)  # send quit command 'q' (player must not use '--no-keys' option)
                self.process.terminate()
                self.process.wait()

                log.info('Player[single] gracefully terminated (%s)' % self.process.returncode)
                return self.process.returncode
            except EnvironmentError as e:
                logger.error("Can't stop player[single] %s: %s", self.uri, e)

        self.process = None
        return None
