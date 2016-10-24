import logging
import os
from subprocess import Popen, PIPE, STDOUT
import time
import subprocess

from cfgviewer.cfgpanel.constants import MAX_CAM_AMOUNT
from log import log

BASH_SHEBANG = '#!/usr/bin/env bash\n'
KEY_OMXPLAYER_QUIT = 'q'
PLAYER_NAME = 'omxplayer'
DEV_NULL = open(os.devnull, 'w')

PROC_CHECK_INTERVAL_S = 2

logger = logging.getLogger(__name__)


class PlayerSplit:
    def __init__(self, config_array_4, win_array_4):
        self.total_stream_count = 0
        self.cam_configs = config_array_4
        self.win_info = win_array_4
        self.stream_command = []
        self.check_counter = []

        self.auto_restart_enabled = True
        self.wait_process = None

    def play(self, statuses):
        for i in range(0, MAX_CAM_AMOUNT):
            # prepare starting command for Omxplayer
            log.info('Setting up Players[split-%d]...' % i)
            cam_config = self.cam_configs[i]
            address = cam_config.address
            win = self.win_info[i]
            cam_no = i + 1
            screen_name = 'camera%d' % cam_no
            if not address:
                url = '/home/haso/camviewer/not_configured.mp4'
                cmd = "'omxplayer --adev hdmi --timeout 5 --blank --no-osd --loop --win %s %s'" % (win, url)
            else:
                url = cam_config.sub_stream_url()
                cmd = "omxplayer --adev hdmi --timeout 5 --blank --live --aspect-mode fill --avdict rtsp_transport:tcp --win %s \"%s\"" % (win, url)
                self.total_stream_count += 1

            script_path = '/home/haso/camviewer/start%d.sh' % i
            f = open(script_path, 'w+')
            f.write(BASH_SHEBANG)
            f.write(cmd + '\n')
            f.truncate()
            f.close()
            log.info('Stream[%d] - %s - start script prepared: (%s).' % (i, url, script_path))

            # execute starting command
            command = ['screen', '-dmS', screen_name, "sh", script_path]
            self.stream_command.append(command)
            self.check_counter.append(0)
            Popen(command, stdin=PIPE, stdout=DEV_NULL, stderr=STDOUT, close_fds=True, bufsize=0)  # async. execution, instant exit
            log.info('Player[split-%d] started with command: (%s)' % (i, repr(command)))

        # restart player not running anymore and stop was not requested
        while self.auto_restart_enabled:
            # wait before check...
            time.sleep(PROC_CHECK_INTERVAL_S)

            requiring_restart = []
            log.info("Checking streams amount...")
            for i in range(0, MAX_CAM_AMOUNT):
                cam_no = i + 1
                screen_name = 'camera%d' % cam_no
                ps_full_list = subprocess.Popen(['ps', '-ef'], stdout=subprocess.PIPE)
                ps_full_list.wait()
                ps_filtered = subprocess.Popen(['grep', '[c]amera%d' % cam_no], stdin=ps_full_list.stdout, stdout=subprocess.PIPE)
                ps_filtered.wait()

                related_processes_amnt = subprocess.check_output(['wc', '-l'], stdin=ps_filtered.stdout)
                log.info(" -- camera[%d] related process check [%d] processes found = %s." % (cam_no, self.check_counter[i], related_processes_amnt.rstrip('\n')))
                self.check_counter[i] += 1

                if related_processes_amnt is not None and int(related_processes_amnt) != 1 and self.auto_restart_enabled:
                    log.info(' --- Player[split-%d] requires restart.' % i)
                    requiring_restart.append(i)
                elif self.check_counter[i] % 1800 == 0:  # every 1800 checks. (every 1h) restart stream even if it is still running (workaround for image freezing after w while)
                    log.info(' --- Player[split-%d] periodic restart - counter = %s.' % (i, self.check_counter[i]))

                    # stop player first
                    ps_full_list = subprocess.Popen(['ps', '-ef'], stdout=subprocess.PIPE)
                    ps_full_list.wait()
                    ps_filtered = subprocess.Popen(['grep', '[c]amera%d' % cam_no], stdin=ps_full_list.stdout, stdout=subprocess.PIPE)
                    ps_filtered.wait()
                    ps_filtered = subprocess.Popen(['grep', '%s' % self.win_info[i]], stdin=ps_filtered.stdout, stdout=subprocess.PIPE)
                    ps_filtered.wait()
                    get_pid = subprocess.Popen(['awk', '{print $2}'], stdin=ps_filtered.stdout, stdout=subprocess.PIPE)
                    get_pid.wait()
                    kill_process = subprocess.Popen(['xargs', '-n', '1', 'sudo', 'kill', '-s', 'SIGINT'], stdin=get_pid.stdout, stdout=subprocess.PIPE)
                    kill_process.wait()
                    kill_screen = subprocess.Popen(['screen', '-X', '-S', screen_name, 'kill'], stdin=get_pid.stdout, stdout=subprocess.PIPE)
                    kill_screen .wait()
                    log.info(' --- Player[split-%d] killed.')

                    Popen(self.stream_command[i], stdin=PIPE, stdout=DEV_NULL, stderr=STDOUT, close_fds=True, bufsize=0)  # async. execution, instant exit
                    self.check_counter[i] = 0

            if len(requiring_restart) < self.total_stream_count:
                # restart stream if needed
                for i in requiring_restart:
                    command = self.stream_command[i]
                    Popen(command, stdin=PIPE, stdout=DEV_NULL, stderr=STDOUT, close_fds=True, bufsize=0)  # async. execution, instant exit
                    log.info(' --- Player[split-%d] restarted.' % i)
            else:
                log.info(' --- Player[split] >>> All streams are down (or none is configured)...')
                self.disable_auto_restart()

                kill_all_omx_processes()  # showing 1-4 x 'not_configured.mp4' are also omx processes

                # invoke script that will return the control when all streams stop
                command = ['bash', '/home/haso/camviewer/wait_for_omx.sh']
                log.info('Starting wait_for_omx[split] script... (%s)' % repr(command))
                self.wait_process = Popen(command, stdin=PIPE, stdout=DEV_NULL, stderr=STDOUT, close_fds=True, bufsize=0)  # async. execution, instant exit
                self.wait_process.wait()
                log.info('Player[split] stopped.')
                break

    def disable_auto_restart(self):
        self.auto_restart_enabled = False


def kill_all_omx_processes():
    command = ['bash', '/home/haso/camviewer/stop4.sh']
    log.info("Stopping all omxplayer processes in Player[split], cmd=(%s)" % command)
    Popen(command, stdin=PIPE, stdout=DEV_NULL, stderr=STDOUT, close_fds=True, bufsize=0)
