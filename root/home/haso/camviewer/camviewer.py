#!/usr/bin/env python
# coding=utf-8

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

import getpass
import os.path
import time
from subprocess import Popen, PIPE, STDOUT
from Queue import Queue
from threading import Timer

from fysom import Fysom

import event_handler
import info_collector
import info_window
from cfgviewer.cfgpanel.constants import AUTO_CLOSE_TIME, CYCLE_TIME_DEFAULT, WIN_SINGLE, CFG_CAM_IP_FILENAME, CYCLE_TIME_MAX_INCR, EMPTY_CONFIG_CONTENT, CAM_STATUS_OK
from dbus_omxplayer import send_dbus_stop, OMXPlayerStopError
from log_config import log
from player import Player, DEV_NULL
from player_split import PlayerSplit, kill_all_omx_processes
from utils import NAME_MODE_SINGLE, NAME_MODE_SPLIT, NAME_MODE_AUTO, MODE_SINGLE, MODE_SPLIT, MODE_AUTO

_FSM_TRANSITION_ = 'name'
_FSM_SRC_ = 'src'
_FSM_DST_ = 'dst'

TRANSITION_INIT = 'init'
TRANSITION_INFO = 'show_info'
TRANSITION_CAM_SINGLE = 'view_cam_single'
TRANSITION_CAM_SPLIT = 'view_cam_split'
TRANSITION_CAM_AUTO = 'view_cam_auto'

STATE_SYSINFO = 'SysInfo'
STATE_STREAMING_SINGLE = 'StreamingSingle'
STATE_STREAMING_SPLIT = 'StreamingSplit'
STATE_STREAMING_AUTO = 'StreamingAuto'

fsm = Fysom({
    'initial': {'state': STATE_SYSINFO, 'event': TRANSITION_INIT, 'defer': True},
    'events':
        [
            {_FSM_TRANSITION_: TRANSITION_INFO, _FSM_SRC_: STATE_STREAMING_SINGLE, _FSM_DST_: STATE_SYSINFO},
            {_FSM_TRANSITION_: TRANSITION_INFO, _FSM_SRC_: STATE_STREAMING_SPLIT, _FSM_DST_: STATE_SYSINFO},
            {_FSM_TRANSITION_: TRANSITION_INFO, _FSM_SRC_: STATE_STREAMING_AUTO, _FSM_DST_: STATE_SYSINFO},
            {_FSM_TRANSITION_: TRANSITION_CAM_SINGLE, _FSM_SRC_: STATE_SYSINFO, _FSM_DST_: STATE_STREAMING_SINGLE},
            {_FSM_TRANSITION_: TRANSITION_CAM_SPLIT, _FSM_SRC_: STATE_SYSINFO, _FSM_DST_: STATE_STREAMING_SPLIT},
            {_FSM_TRANSITION_: TRANSITION_CAM_AUTO, _FSM_SRC_: STATE_SYSINFO, _FSM_DST_: STATE_STREAMING_AUTO}
        ]
})


def stop_single_omx_dbus():
    try:
        send_dbus_stop()
    except OMXPlayerStopError:
        log.info('ERROR: Could not stop OMXPlayer through DBUS.')


def full_reboot():
    kill_all_omx_processes()

    command = ['sudo', '/usr/bin/fbi', '-T', '1', '--noverbose', '-a', '/home/haso/camviewer/rebooting.jpg']
    Popen(command, stdin=PIPE, stdout=DEV_NULL, stderr=STDOUT, close_fds=True, bufsize=0)
    time.sleep(3)

    command = ['sudo', 'reboot']
    log.info("Rebooting device with cmd=(%s)" % command)
    Popen(command, stdin=PIPE, stdout=DEV_NULL, stderr=STDOUT, close_fds=True, bufsize=0)


# noinspection PyMethodMayBeStatic
class Camviewer:
    _info_collector_thread = info_collector.InfoCollectorThread()
    _event_handler_thread = event_handler.EventHandlerThread()
    _transitions_queue = Queue()
    _cam_stop_user_request = True  # we cannot distinguish
    _streaming = True
    _auto_close_timer = None
    _cycle_time = CYCLE_TIME_DEFAULT
    _mode = None

    def __init__(self):
        self._player_split = None

        self._info_collector_thread.start()
        self._info_window_ref = info_window.create(self._info_collector_thread)
        self._set_mode(MODE_SPLIT)

        self._event_handler_thread.set_esc_handler(self.action_button_esc)
        self._event_handler_thread.set_up_handler(self.action_handle_up)
        self._event_handler_thread.set_down_handler(self.action_button_down)
        self._event_handler_thread.set_enter_handler(self.action_handle_enter)
        self._event_handler_thread.set_left_handler(self.action_handle_left)
        self._event_handler_thread.set_right_handler(self.action_handle_right)

        self._event_handler_thread.start()

    def _async_transition(self, transition_name):
        log.info('Storing transition: %s [%s]' % (fsm.current, transition_name))
        self._transitions_queue.put(transition_name)

    def _set_mode(self, mode):
        self._mode = mode

        # Update mode name on info screen too
        if mode == MODE_SINGLE:
            self._info_window_ref.set_mode_name(MODE_SINGLE, NAME_MODE_SINGLE)
        elif mode == MODE_SPLIT:
            self._info_window_ref.set_mode_name(MODE_SPLIT, NAME_MODE_SPLIT)
        elif mode == MODE_AUTO:
            self._info_window_ref.set_mode_name(MODE_AUTO, '%s [co %d sekund]' % (NAME_MODE_AUTO, int(self._cycle_time)))
        else:
            log.error("Invalid mode given: (%s)" % mode)

    def main_control_loop(self):
        fsm.onSysInfo = self.on_state_sys_info
        fsm.onStreamingSingle = self.on_state_streaming_single
        fsm.onStreamingSplit = self.on_state_streaming_split
        fsm.onStreamingAuto = self.on_state_streaming_auto

        self._async_transition(TRANSITION_INIT)  # [NONE] ==init==> [SysInfo]

        while True:
            log.info('Waiting for transition...')
            transition_name = self._transitions_queue.get(block=True)

            # execute transition - using 'Hollywood principle' in flow control
            if fsm.can(transition_name):
                log.info('Executing transition: %s' % transition_name)
                fsm.trigger(transition_name)
            else:
                log.warn('Transition (%s) not allowed in state (%s). Skipping...' % (transition_name, fsm.current))

            self._transitions_queue.task_done()

        log.info("Camviewer app stopped.")
        self._event_handler_thread.stop()
        self._info_collector_thread.stop()
        return

    def auto_sysinfo_close(self):
        current = fsm.current

        any_configured = self._info_collector_thread.is_any_cam()

        log.info("Timer fired (%s)." % current)
        if current == STATE_SYSINFO and any_configured:
            log.info("Timer - closing SysInfo.")
            info_window.close()
        else:
            # Check again later
            log.info("Timer - will check again later...")
            self._auto_close_timer = Timer(AUTO_CLOSE_TIME, self.auto_sysinfo_close)
            self._auto_close_timer.start()

    def on_state_sys_info(self, e):
        log.info("Showing sysinfo screen.")

        if self._auto_close_timer is not None:
            self._auto_close_timer.cancel()

        self._auto_close_timer = Timer(AUTO_CLOSE_TIME, self.auto_sysinfo_close)
        self._auto_close_timer.start()

        info_window.show()  # halts here until window is closed...

        log.info("Cancelling auto_close_timer...")
        self._auto_close_timer.cancel()

        log.info("Exiting sysinfo screen.")
        if self._mode == MODE_SINGLE:
            self._async_transition(TRANSITION_CAM_SINGLE)  # [SysInfo] ==view_cam_single==> [StreamingSingle]
        elif self._mode == MODE_SPLIT:
            self._async_transition(TRANSITION_CAM_SPLIT)  # [SysInfo] ==view_cam_split==> [StreamingSplit]
        elif self._mode == MODE_AUTO:
            self._async_transition(TRANSITION_CAM_AUTO)  # [SysInfo] ==view_cam_auto==> [StreamingAuto]
        else:
            log.error("Unknown mode: (%s)" % self._mode)

    def on_state_streaming_single(self, e):
        log.info('Entering state StreamingSingle.')
        self._streaming = True
        self.handle_player_single()
        log.info('Exiting state StreamingSingle.')
        self._async_transition(TRANSITION_INFO)  # [StreamingSingle] ==show_info==> [SysInfo]

    def on_state_streaming_split(self, e):
        log.info('Entering state StreamingSplit.')
        self._streaming = True
        self.handle_player_split()
        log.info('Exiting state StreamingSplit.')
        self._async_transition(TRANSITION_INFO)  # [StreamingSplit] ==show_info==> [SysInfo]

    def on_state_streaming_auto(self, e):
        log.info('Entering state StreamingAuto.')
        self._streaming = True
        self.handle_player_auto()
        log.info('Exiting state StreamingAuto.')
        self._async_transition(TRANSITION_INFO)  # [StreamingAuto] ==show_info==> [SysInfo]

    def handle_player_single(self):
        while self._streaming:
            cams_configs = self._info_collector_thread.cams_configs  # not all cams might have been found on startup
            self._cam_stop_user_request = False

            any_stream = False
            for i in range(0, len(cams_configs)):
                cam_config = cams_configs[i]
                if cam_config.address:
                    status = self._info_collector_thread.cams_statuses[i]
                    if status == CAM_STATUS_OK:
                        any_stream = True
                        log.info('Starting Player[single] on address: (%s)' % cam_config.main_stream_url())
                        player_single = Player(i, cam_config.main_stream_url(), WIN_SINGLE)
                        player_single.play()
                        player_single.wait_to_finish()  # if closed switch automatically to another

                        if not self._streaming:  # streaming mode exit was requested
                            break
                    else:
                        log.info('Skipping Player[single] camera address: (%s). Not accessible.' % cam_config.main_stream_url())
                        player_single = Player(i, '/home/haso/camviewer/no_signal.mp4', WIN_SINGLE, False)
                        player_single.play()
                        player_single.wait_to_finish()
                        continue
                else:
                    log.info('Skipping Player[single] camera address: (%s). Not configured.' % cam_config.main_stream_url())
                    continue

            # After full cycle
            if self._cam_stop_user_request and any_stream:
                log.info("Player[single] stopped manually. Continuing...")
                continue  # cycle again through all cams
            else:
                log.info("Player[single] stopped by itself. Exiting...")
                break  # stream was closed (show info screen)

    def handle_player_auto(self):
        while self._streaming:
            cams_configs = self._info_collector_thread.cams_configs  # not all cams might have been found on startup
            cam_statuses = self._info_collector_thread.cams_statuses
            any_stream = False
            for i in range(0, len(cams_configs)):
                self._cam_stop_user_request = False
                cam_config = cams_configs[i]
                if cam_config.address:
                    status = cam_statuses[i]
                    if status == CAM_STATUS_OK:
                        any_stream = True
                        log.info('Starting Player[auto] on address: (%s)' % cam_config.main_stream_url())
                        player_single = Player(i, cam_config.main_stream_url(), WIN_SINGLE)
                        player_single.play()
                        cycle_close_timer = Timer(self._cycle_time, self.stop_auto_cycle)
                        cycle_close_timer.start()
                        player_single.wait_to_finish()
                        cycle_close_timer.cancel()

                        if self._cam_stop_user_request:
                            log.info("Player[auto] stopped by timer. Continuing...")
                            continue  # Closed by timer
                        else:
                            log.info("Player[auto] stopped by itself. Exiting...")
                            self._streaming = False
                            break  # stream was closed (show info screen)
                    else:
                        log.info('Skipping Player[auto] camera address: (%s). Not accessible.' % cam_config.main_stream_url())
                        player_single = Player(i, '/home/haso/camviewer/no_signal.mp4', WIN_SINGLE, False)
                        player_single.play()
                        player_single.wait_to_finish()
                else:
                    log.info('Skipping Player[auto] camera address: (%s). Not configured.' % cam_config.main_stream_url())
                    continue
            if not any_stream:
                log.info("Player[auto] stopped because no stream was accessible. Exiting...")
                break

    def stop_auto_cycle(self):
        self._cam_stop_user_request = True
        stop_single_omx_dbus()

    def handle_player_split(self):
        self._cam_stop_user_request = False
        cams_configs = self._info_collector_thread.cams_configs

        self._player_split = PlayerSplit(cams_configs)
        self._player_split.play()

        if self._cam_stop_user_request:
            log.info("Player[split] stopped manually. Done.")
        else:
            log.info("Player[split] exited by itself.")
            kill_all_omx_processes()

    def action_button_esc(self):
        log.info('Handle ESC - begin.')
        if fsm.current == STATE_STREAMING_SINGLE:
            self._stop_streaming_single()
        elif fsm.current == STATE_STREAMING_SPLIT:
            self._stop_streaming_split()
        elif fsm.current == STATE_STREAMING_AUTO:
            self._stop_streaming_auto()
        else:
            log.info('\tHandle ESC - skipped in state (%s).' % fsm.current)
        log.info('Handle ESC - end.')

    def action_handle_up(self):
        log.info('Handle UP - begin.')
        log.info(' - Simulating ESC button to stop whatever is currently streamed...')
        self.action_button_esc()
        full_reboot()
        log.info('Handle UP - end.')

    def action_handle_left(self):
        log.info('Handle LEFT - begin.')
        if fsm.current == STATE_SYSINFO:
            self._decrease_time()
        elif fsm.current == STATE_STREAMING_SINGLE:
            self._next_stream_single()
        else:
            log.info('\tHandle LEFT - skipped in state (%s).' % fsm.current)
        log.info('Handle LEFT - end.')

    def action_handle_right(self):
        log.info('Handle RIGHT - begin.')
        if fsm.current == STATE_SYSINFO:
            self._increase_time()
        elif fsm.current == STATE_STREAMING_SINGLE:
            self._next_stream_single()
        else:
            log.info('\tHandle RIGHT - skipped in state (%s).' % fsm.current)
        log.info('Handle RIGHT - end.')

    def action_button_down(self):
        log.info('Handle DOWN - begin.')
        if fsm.current == STATE_SYSINFO:
            self._change_mode()
        else:
            log.info('\tHandle DOWN - skipped in state (%s).' % fsm.current)
        log.info('Handle DOWN - end.')

    def action_handle_enter(self):
        log.info('Handle ENTER - begin.')
        if fsm.current == STATE_STREAMING_SINGLE:
            self._next_stream_single()
        elif fsm.current == STATE_SYSINFO:
            self._exit_sysinfo()
        else:
            log.info('\tHandle ENTER - skipped in state (%s).' % fsm.current)
        log.info('Handle ENTER - end.')

    def _exit_sysinfo(self):
        log.info('\tClosing SysInfo window to start streaming.')
        info_window.close()

    def _change_mode(self):
        log.info('Current mode: (%s).' % self._mode)
        if self._mode == MODE_SINGLE:
            log.info('\tChanging mode to SPLIT.')
            self._set_mode(MODE_SPLIT)
        elif self._mode == MODE_SPLIT:
            log.info('\tChanging mode to AUTO.')
            self._set_mode(MODE_AUTO)
        elif self._mode == MODE_AUTO:
            log.info('\tChanging mode to SINGLE.')
            self._set_mode(MODE_SINGLE)
        else:
            log.info('Invalid mode detected. Skipping <DOWN> btn.')

    def _next_stream_single(self):
        log.info('\tStopping OMXplayer to go to next cam.')
        self._cam_stop_user_request = True
        stop_single_omx_dbus()

    def _stop_streaming_single(self):
        log.info('\tStopping streaming[single] to show sys info.')
        self._streaming = False
        stop_single_omx_dbus()

    def _stop_streaming_split(self):
        log.info('\tStopping streaming[split] to show sys info.')
        self._player_split.disable_auto_restart()
        self._streaming = False
        self._cam_stop_user_request = True
        kill_all_omx_processes()

    def _stop_streaming_auto(self):
        log.info('\tStopping streaming[auto] to show sys info.')
        self._streaming = False
        stop_single_omx_dbus()

    def _decrease_time(self):
        if self._cycle_time > 1200:
            self._cycle_time -= 600
        elif self._cycle_time > 300:
            self._cycle_time -= 60
        elif self._cycle_time > 120:
            self._cycle_time -= 30
        elif self._cycle_time > 60:
            self._cycle_time -= 15
        elif self._cycle_time > 30:
            self._cycle_time -= 10
        elif self._cycle_time > CYCLE_TIME_DEFAULT:
            self._cycle_time -= 5

        self._set_mode(self._mode)  # Update mode information

    def _increase_time(self):
        if self._cycle_time < 30:
            self._cycle_time += 5
        elif self._cycle_time < 60:
            self._cycle_time += 10
        elif self._cycle_time < 120:
            self._cycle_time += 15
        elif self._cycle_time < 300:
            self._cycle_time += 30
        elif self._cycle_time < 1200:
            self._cycle_time += 60
        elif self._cycle_time < CYCLE_TIME_MAX_INCR:
            self._cycle_time += 600

        self._set_mode(self._mode)  # Update mode information


def main():
    log.info("Starting CAMVIEWER as (%s)..." % getpass.getuser())
    log.info('Working dir (%s)' % os.system('pwd'))
    log.info('Disabling screensaver result (%s)' % os.system('%s %s %s' % ('xset', 's', 'off')))
    log.info('Setting screensaver noblank result (%s)' % os.system('%s %s %s' % ('xset', 's', 'noblank')))
    log.info('Disabling DPMS result (%s)' % os.system('%s %s' % ('xset', '-dpms')))

    cam_config_exists = os.path.isfile(CFG_CAM_IP_FILENAME)
    if cam_config_exists:
        pass
    else:
        log.info("Cameras not configured. Creating an empty config file...")
        with open(CFG_CAM_IP_FILENAME, "w+") as f:
            f.write(EMPTY_CONFIG_CONTENT)
            f.close()

    camviewer = Camviewer()
    camviewer.main_control_loop()
    log.info("Camviewer mainloop finished.")
    exit(0)


if __name__ == "__main__":
    main()
