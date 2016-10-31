import logging
import os
import time
from subprocess import Popen, PIPE, STDOUT, check_output

from log_config import log
from dbus_omxplayer import send_dbus_action, ACTION_POS

VIDEO_NOT_CONFIGURED = 'not_configured.mp4'

SCRIPT_OMX_COUNT = "omx_count.sh"
SCRIPT_OMX_KILL_ALL = 'omx_kill_all.sh'
SCRIPT_OMX_KILL_SINGLE = "omx_kill_single.sh"

BASH_SHEBANG = '#!/usr/bin/env bash\n'
DEV_NULL = open(os.devnull, 'w')
SCREEN_NAME_PATTERN = 'camera%d'

PROC_CHECK_INTERVAL_S = 5
PERIODIC_RESTART_EVERY_CHECK = 720

logger = logging.getLogger(__name__)


class Playstreamation:
    def __init__(self, cam_streams_array_4, win_coords_array_4):
        self.cam_streams = cam_streams_array_4
        self.win_coords = win_coords_array_4
        self.start_commands = []
        self.stream_position = []
        self.check_counters = []
        self.restart_counters = []

        self.auto_restart_enabled = True

    def play(self):
        for stream_id in range(0, len(self.cam_streams)):
            start_cmd = self.prepare_player_start_command(stream_id)

            self.start_commands.append(start_cmd)
            self.check_counters.append(0)
            self.restart_counters.append(0)

            self.start_player(stream_id)

        while self.auto_restart_enabled:
            # periodically restart players that are not running anymore (e.g. there was no connectivity for a moment)
            try:
                time.sleep(PROC_CHECK_INTERVAL_S)
            except KeyboardInterrupt:
                log.info("Exiting...")
                self.auto_restart_enabled = False
                kill_all_omx_processes()
                break

            log.info("Checking if streams are working...")
            streams_to_start = []
            for stream_id in range(0, len(self.cam_streams)):
                win_coords = self.win_coords[stream_id]

                omx_proc_count = check_output(['bash', SCRIPT_OMX_COUNT, win_coords])
                ps_count = omx_proc_count.rstrip('\n')

                self.check_counters[stream_id] += 1
                check_number = self.check_counters[stream_id]
                instance_no = self.restart_counters[stream_id]

                pos_previous = self.stream_position[stream_id]

                if omx_proc_count is not None:
                    stream_freeze_detected = False
                    proc_count_int = int(omx_proc_count)
                    if proc_count_int == 1:
                        if pos_previous >= 0:
                            # noinspection PyBroadException
                            try:
                                pos = send_dbus_action(stream_id, ACTION_POS)
                                self.stream_position[stream_id] = pos

                                if pos_previous == pos:
                                    stream_freeze_detected = True
                            except BaseException:
                                pos = '[unknown]'
                        else:
                            pos = '[not tracking]'
                    else:
                        pos = '[instances issue]'

                    log.info(" -- Player[stream-%d/%d] check %d proc=%s pos=%s freeze detected=%s" % (stream_id, instance_no, check_number, ps_count, pos, stream_freeze_detected))
                    if self.auto_restart_enabled:
                        if proc_count_int == 0:
                            log.info(' --- Player[stream-%d/%d] not running - scheduling start...' % (stream_id, check_number))
                            streams_to_start.append(stream_id)
                        elif proc_count_int > 1:
                            # just recover from glitches with many players opened for single stream (should not happen)
                            log.info(' --- Player[stream-%d/%d] running in too many instances - killing all and scheduling start.' % (stream_id, check_number))
                            kill_single_omx_window(stream_id, win_coords)
                            streams_to_start.append(stream_id)
                        elif proc_count_int == 1:
                            if stream_freeze_detected:
                                log.info(' --- Player[stream-%d/%d] stream freeze detected - immediate restart.' % (stream_id, check_number))
                                self.player_immediate_restart(stream_id, win_coords)
                            elif check_number % PERIODIC_RESTART_EVERY_CHECK == 0:  # restart stream periodically even if it is still running (workaround for image freezing after w while)
                                log.info(' --- Player[stream-%d/%d] performing periodic instant restart.' % (stream_id, check_number))
                                self.player_immediate_restart(stream_id, win_coords)
                        else:
                            pass  # keep playing
                else:
                    log.error('Invalid processes count received (None).')

            log.info('Performing scheduled starts...')

            # try to start scheduled streams
            for stream_id_to_start in streams_to_start:
                self.start_player(stream_id_to_start)

    def prepare_player_start_command(self, i):
        # prepare starting script for omxplayer in proper window
        log.info('Setting up Players[stream-%d]...' % i)

        stream_url = self.cam_streams[i]
        win_coords = self.win_coords[i]
        screen_name = SCREEN_NAME_PATTERN % i
        dbus_name = "org.mpris.MediaPlayer2.omxplayer.%s" % screen_name

        if not stream_url:
            url = VIDEO_NOT_CONFIGURED
            cmd = "omxplayer --adev hdmi --aidx -1 --timeout 5 --blank --no-keys --no-osd --loop --win %s --dbus_name %s %s" % (win_coords, dbus_name, url)
            # NOTE: allowed options are either --live or --no-osd and not both
            self.stream_position.append(-1)
        else:
            url = stream_url
            cmd = "omxplayer --adev hdmi --aidx -1 --timeout 5 --blank --no-keys --live --aspect-mode fill --avdict rtsp_transport:tcp --win %s --dbus_name %s \"%s\"" % (win_coords, dbus_name, url)  # quotes around stream are required in some cases
            self.stream_position.append(0)
        log.info(' - Player[stream-%d] - omx command: (%s).' % (i, cmd))

        script_path = './start%d.sh' % i
        store_as_script_on_disk(i, cmd, script_path)

        # prepare starting commands for current script
        start_cmd = ['screen', '-dmS', screen_name, "sh", script_path]
        log.info(' - Player[stream-%d] - start command: (%s).' % (i, start_cmd))
        return start_cmd

    def player_immediate_restart(self, stream_id, win_coords):
        kill_single_omx_window(stream_id, win_coords)
        self.start_player(stream_id)

    def start_player(self, i):
        player_start_command = self.start_commands[i]
        Popen(player_start_command, stdin=PIPE, stdout=DEV_NULL, stderr=STDOUT, close_fds=True, bufsize=0)  # async. execution, instant exit
        self.check_counters[i] = 0
        self.restart_counters[i] += 1
        if self.stream_position[i] > 0:
            self.stream_position[i] = 0
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


def main_for_testing():
    cam_streams = [
        "",
        "rtsp://172.16.1.195:554/av0_1",  # rtsp://mpv.cdn3.bigCDN.com:554/bigCDN/mp4:bigbuckbunnyiphone_400.mp4
        "rtsp://172.16.1.190:554/av0_1",  # some address where there is no stream
        "rtsp://172.16.1.196:554/av0_1"   # rtsp://mm2.pcslab.com/mm/7h2000.mp4
    ]

    win_coords = [
        '0,0,528,298',
        '532,0,1060,298',
        '0,302,528,600',
        '532,302,1060,600'
    ]

    player = Playstreamation(cam_streams, win_coords)
    player.play()


if __name__ == "__main__":
    main_for_testing()
