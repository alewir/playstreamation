import logging
import os
import time
from subprocess import Popen, PIPE, STDOUT, check_output

from log_config import log

HOME_DIR = '/home/haso/camviewer/'
VIDEO_NOT_CONFIGURED = 'not_configured.mp4'

SCRIPT_OMX_WAIT = 'omx_wait.sh'
SCRIPT_OMX_COUNT = "omx_count.sh"
SCRIPT_OMX_KILL_ALL = 'omx_kill_all.sh'
SCRIPT_OMX_KILL_SINGLE = "omx_kill_single.sh"

BASH_SHEBANG = '#!/usr/bin/env bash\n'
DEV_NULL = open(os.devnull, 'w')
SCREEN_NAME_PATTERN = 'camera%d'

PROC_CHECK_INTERVAL_S = 5
PERIODIC_RESTART_EVERY_CHECK = 720

# These depends on actual screen used - should be calculated somehow
WIN_0 = '0,0,528,298'
WIN_1 = '532,0,1060,298'
WIN_2 = '0,302,528,600'
WIN_3 = '532,302,1060,600'
WIN_COORDS = [WIN_0, WIN_1, WIN_2, WIN_3]

logger = logging.getLogger(__name__)


class PlayerSplit:
    def __init__(self, cam_configs_array_4):
        self.cam_configs = cam_configs_array_4
        self.start_commands = []
        self.check_counters = []
        self.restart_counters = []

        self.auto_restart_enabled = True
        self.total_stream_count = 0

    def play(self):
        for stream_id in range(0, len(self.cam_configs)):
            start_cmd = self.prepare_player_start_command(stream_id)

            self.start_commands.append(start_cmd)
            self.check_counters.append(0)
            self.restart_counters.append(0)

            self.start_player(stream_id)

        while self.auto_restart_enabled:
            # periodically restart players that are not running anymore (e.g. there was no connectivity for a moment)
            time.sleep(PROC_CHECK_INTERVAL_S)

            log.info("Checking if streams are working...")
            streams_to_start = []
            for stream_id in range(0, len(self.cam_configs)):
                win_coords = WIN_COORDS[stream_id]
                omx_proc_count = check_output(['bash', SCRIPT_OMX_COUNT, win_coords])

                self.check_counters[stream_id] += 1
                check_number = self.check_counters[stream_id]
                instance_no = self.restart_counters[stream_id]
                log.info(" -- Player[stream-%d/%d] process check %d processes found=%s" % (stream_id, instance_no, check_number, omx_proc_count.rstrip('\n')))
                if omx_proc_count is not None and self.auto_restart_enabled:
                    proc_count_int = int(omx_proc_count)
                    if proc_count_int == 0:
                        log.info(' --- Player[stream-%d] not running - scheduling start...' % stream_id)
                        streams_to_start.append(stream_id)
                    elif proc_count_int > 1:
                        # just recover from glitches with many players opened for single stream (should not happen)
                        log.info(' --- Player[stream-%d] running in too many instances - killing all and scheduling start.' % stream_id)
                        kill_single_omx_window(stream_id, win_coords)
                        streams_to_start.append(stream_id)
                    elif proc_count_int == 1 and check_number % PERIODIC_RESTART_EVERY_CHECK == 0:
                        # restart stream periodically even if it is still running (workaround for image freezing after w while)
                        log.info(' --- Player[stream-%d] scheduling periodic restart for counter=[%d].' % (stream_id, check_number))
                        kill_single_omx_window(stream_id, win_coords)
                        self.start_player(stream_id)  # instant restart
                    else:
                        pass  # keep playing

            if len(streams_to_start) < self.total_stream_count:
                # try to start scheduled streams
                for stream_id_to_start in streams_to_start:
                    self.start_player(stream_id_to_start)
            else:
                # something is wrong - stopping players for all streams and exiting...
                log.info(' --- Player[split] >>> All streams are down (or none is configured)...')
                self.disable_auto_restart()

                kill_all_omx_processes()  # showing 1-4 streams playing 'not_configured.mp4' are also omx processes and we need to close them

                # invoke script that will return the control when all streams are stopped
                wait_command = ['bash', SCRIPT_OMX_WAIT]
                log.info('Starting omx_wait[split] script... (%s)' % repr(wait_command))
                wait_process = Popen(wait_command, stdin=PIPE, stdout=DEV_NULL, stderr=STDOUT, close_fds=True, bufsize=0)  # async. execution, instant exit
                wait_process.wait()

                log.info('Player[split] stopped.')
                break

    def prepare_player_start_command(self, i):
        # prepare starting script for omxplayer in proper window
        log.info('Setting up Players[stream-%d]...' % i)

        cam_config = self.cam_configs[i]
        address = cam_config.address
        win_coords = WIN_COORDS[i]
        screen_name = SCREEN_NAME_PATTERN % i
        dbus_name = "org.mpris.MediaPlayer2.omxplayer.%s" % screen_name

        if not address:
            url = HOME_DIR + VIDEO_NOT_CONFIGURED
            cmd = "omxplayer --adev hdmi --aidx -1 --timeout 5 --blank --no-keys --no-osd --loop --win %s --dbus_name %s %s" % (win_coords, dbus_name, url)
            # NOTE: allowed options are either --live or --no-osd and not both
        else:
            url = cam_config.sub_stream_url()
            cmd = "omxplayer --adev hdmi --aidx -1 --timeout 5 --blank --no-keys --live --aspect-mode fill --avdict rtsp_transport:tcp --win %s --dbus_name %s \"%s\"" % (win_coords, dbus_name, url)  # quotes around stream are required in some cases
            self.total_stream_count += 1
        log.info(' - Player[stream-%d] - omx command: (%s).' % (i, cmd))

        script_path = HOME_DIR + ('start%d.sh' % i)
        store_as_script_on_disk(i, cmd, script_path)

        # prepare starting commands for current script
        start_cmd = ['screen', '-dmS', screen_name, "sh", script_path]
        log.info(' - Player[stream-%d] - start command: (%s).' % (i, start_cmd))
        return start_cmd

    def start_player(self, i):
        player_start_command = self.start_commands[i]
        Popen(player_start_command, stdin=PIPE, stdout=DEV_NULL, stderr=STDOUT, close_fds=True, bufsize=0)  # async. execution, instant exit
        self.check_counters[i] = 0
        self.restart_counters[i] += 1
        log.info(' --- Player[stream-%d] started with command: (%s)' % (i, repr(player_start_command)))

    def disable_auto_restart(self):
        self.auto_restart_enabled = False


def store_as_script_on_disk(i, content, script_path):
    f = open(script_path, 'w+')
    f.write(BASH_SHEBANG)
    f.write(content + '\n')
    f.truncate()
    f.close()
    log.info(' - Player[stream-%d] - start script stored on disk: (%s).' % (i, script_path))


def kill_single_omx_window(i, win_coords_filter):
    screen_name_filter = SCREEN_NAME_PATTERN % i
    kill_single_command = ['bash', SCRIPT_OMX_KILL_SINGLE, win_coords_filter, screen_name_filter]
    log.info(' --- Player[stream-%d] stopping players for single window, cmd=(%s)' % (i, kill_single_command))
    kill_result = check_output(kill_single_command)
    log.info(' --- Player[stream-%d] kill single window result: (\n%s)', i, kill_result)


def kill_all_omx_processes():
    kill_all_command = ['bash', SCRIPT_OMX_KILL_ALL]
    log.info(" --- Player - stopping players for all windows, cmd=(%s)" % kill_all_command)
    kill_result = check_output(kill_all_command)
    log.info(' --- Player - kill all windows result: (%s)', kill_result)
