import logging
import os
from subprocess import Popen, PIPE, STDOUT
import time
import subprocess

from cfgviewer.cfgpanel.constants import MAX_CAM_AMOUNT
from log import log

SCRIPT_OMX_WAIT = 'omx_wait.sh'
SCRIPT_OMX_COUNT = "omx_count.sh"
SCRIPT_OMX_KILL_SINGLE = "omx_kill_single.sh"
SCRIPT_OMX_KILL_ALL = 'omx_kill_all.sh'

BASH_SHEBANG = '#!/usr/bin/env bash\n'
KEY_OMXPLAYER_QUIT = 'q'
PLAYER_NAME = 'omxplayer'
DEV_NULL = open(os.devnull, 'w')

PROC_CHECK_INTERVAL_S = 5
PERIODIC_RESTART_EVERY_CHECK = 720

logger = logging.getLogger(__name__)


class PlayerSplit:
    def __init__(self, config_array_4, win_array_4):
        self.total_stream_count = 0
        self.cam_configs = config_array_4
        self.win_info = win_array_4
        self.start_commands = []
        self.check_counters = []

        self.auto_restart_enabled = True

    def play(self):
        for stream_id in range(0, MAX_CAM_AMOUNT):
            start_cmd = self.prepare_player_start_command(stream_id)

            self.start_commands.append(start_cmd)
            self.check_counters.append(0)

            self.start_player(stream_id)

        while self.auto_restart_enabled:
            # periodically restart players that are not running anymore if stop was not requested
            time.sleep(PROC_CHECK_INTERVAL_S)

            log.info("Checking if streams are working...")
            streams_to_start = []
            for stream_id in range(0, MAX_CAM_AMOUNT):
                win_coords = self.win_info[stream_id]
                omx_proc_count = subprocess.check_output(['bash', SCRIPT_OMX_COUNT, win_coords])

                self.check_counters[stream_id] += 1
                check_number = self.check_counters[stream_id]
                log.info(" -- Player[split-%d] related process check [%d] processes count = %s." % (stream_id, check_number, omx_proc_count.rstrip('\n')))
                if omx_proc_count is not None and self.auto_restart_enabled:
                    proc_count_int = int(omx_proc_count)
                    if proc_count_int == 0:
                        log.info(' --- Player[split-%d] not running - scheduling start...' % stream_id)
                        streams_to_start.append(stream_id)
                    elif proc_count_int > 1:
                        # just recover from glitches with many players opened for single stream
                        log.info(' --- Player[split-%d] running in too many instances - killing all and scheduling start.' % stream_id)
                        kill_single_omx_window(stream_id, win_coords)
                        streams_to_start.append(stream_id)
                    elif proc_count_int == 1 and check_number % PERIODIC_RESTART_EVERY_CHECK == 0:
                        # restart stream even if it is still running (workaround for image freezing after w while)
                        log.info(' --- Player[split-%d] scheduling periodic restart for counter=[%d].' % (stream_id, check_number))
                        kill_single_omx_window(stream_id, win_coords)
                        self.start_player(stream_id)

                    else:
                        pass  # keep playing

            if len(streams_to_start) < self.total_stream_count:
                # some still working - just start scheduled streams
                for stream_id_to_start in streams_to_start:
                    self.start_player(stream_id_to_start)
            else:
                # something is wrong - stopping player
                log.info(' --- Player[split] >>> All streams are down (or none is configured)...')
                self.disable_auto_restart()

                kill_all_omx_processes()  # showing 1-4 streams playing 'not_configured.mp4' are also omx processes and we need to close them

                # invoke script that will return the control when all streams stop
                wait_command = ['bash', SCRIPT_OMX_WAIT]
                log.info('Starting omx_wait[split] script... (%s)' % repr(wait_command))
                wait_process = Popen(wait_command, stdin=PIPE, stdout=DEV_NULL, stderr=STDOUT, close_fds=True, bufsize=0)  # async. execution, instant exit
                wait_process.wait()

                log.info('Player[split] stopped.')
                break

    def prepare_player_start_command(self, i):
        # prepare starting script and command for omxplayer
        log.info('Setting up Players[split-%d]...' % i)

        cam_config = self.cam_configs[i]
        address = cam_config.address
        win_coords = self.win_info[i]

        if not address:
            url = '/home/haso/camviewer/not_configured.mp4'
            cmd = "omxplayer --adev hdmi --timeout 5 --blank --no-osd --loop --win %s %s" % (win_coords, url)
        else:
            url = cam_config.sub_stream_url()
            cmd = "omxplayer --adev hdmi --timeout 5 --blank --live --aspect-mode fill --avdict rtsp_transport:tcp --win %s \"%s\"" % (win_coords, url)
            self.total_stream_count += 1
        log.info(' - Player[split-%d] - omx command: (%s).' % (i, cmd))

        script_path = '/home/haso/camviewer/start%d.sh' % i
        f = open(script_path, 'w+')
        f.write(BASH_SHEBANG)
        f.write(cmd + '\n')
        f.truncate()
        f.close()
        log.info(' - Player[split-%d] - start script prepared: (%s).' % (i, script_path))

        # store starting command
        screen_name = 'camera%d' % (i + 1)
        start_cmd = ['screen', '-dmS', screen_name, "sh", script_path]
        log.info(' - Player[split-%d] - start command: (%s).' % (i, start_cmd))
        return start_cmd

    def start_player(self, i):
        player_start_command = self.start_commands[i]
        Popen(player_start_command, stdin=PIPE, stdout=DEV_NULL, stderr=STDOUT, close_fds=True, bufsize=0)  # async. execution, instant exit
        self.check_counters[i] = 0
        log.info('Player[split-%d] started with command: (%s)' % (i, repr(player_start_command)))

    def disable_auto_restart(self):
        self.auto_restart_enabled = False


def kill_single_omx_window(i, win_coords_filter):
    screen_name_filter = '[c]amera%d' % (i + 1)
    kill_single_command = ['bash', SCRIPT_OMX_KILL_SINGLE, win_coords_filter, screen_name_filter]
    log.info(' --- Player[split-%d] - stopping players for single window, cmd=(%s)' % (i, kill_single_command))
    kill_result = subprocess.check_output(kill_single_command)
    log.info(' --- Player[split-%d] kill single window result: (%s)', i, kill_result)


def kill_all_omx_processes():
    kill_all_command = ['bash', SCRIPT_OMX_KILL_ALL]
    log.info("Player[split] - stopping players for all windows, cmd=(%s)" % kill_all_command)
    kill_result = subprocess.check_output(kill_all_command)
    log.info(' --- Player[split] kill all windows result: (%s)', kill_result)
