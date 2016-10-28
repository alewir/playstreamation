#!/usr/bin/env python
import os
import time
# noinspection PyUnresolvedReferences
import dbus
from log_config import log

DBUS_FILE_NAME_OMXPLAYER = '/tmp/omxplayerdbus.%s' % os.getlogin()
DBUS_RETRY_INTERVAL = 0.2

ACTION_POS = "ACTION_STATUS"
ACTION_PREV = "ACTION_PREVIOUS"
ACTION_STOP = "ACTION_STOP"
ACTION_QUIT = "ACTION_QUIT"


# noinspection PyUnusedLocal
def action_pos(stream_name, if_player, if_props, if_root):
    position = if_props.Position() / 1000000
    return position


# noinspection PyUnusedLocal
def action_stop(stream_name, if_player, if_props, if_root):
    if_player.Stop()
    log.debug('\t\t[%s] - Stop sent to dbus PLAYER interface.' % stream_name)
    return None


# noinspection PyUnusedLocal
def action_prev(stream_name, if_player, if_props, if_root):
    if_player.Previous()
    log.debug('\t\t[%s] - Previous sent to dbus PLAYER interface.' % stream_name)
    return None


# noinspection PyUnusedLocal
def action_quit(stream_name, if_player, if_props, if_root):
    if_root.Quit()
    log.debug('\t\t[%s] - Quit sent to dbus ROOT interface.' % stream_name)
    return None


actions = {
    ACTION_POS: action_pos,
    ACTION_PREV: action_prev,
    ACTION_STOP: action_stop,
    ACTION_QUIT: action_quit
}


def main():
    log.debug('Opening: %s' % DBUS_FILE_NAME_OMXPLAYER)

    for i in range(0, 4):
        try:
            log.debug('stream-%d connecting...' % i)
            action_result = send_dbus_action(i, ACTION_POS)
            log.debug('[stream-%d] action finished. %s' % (i, action_result if action_result is not None else ""))
        except OMXPlayerStopError:
            log.debug('[stream-%d] action failed.' % i)


class OMXPlayerStopError(BaseException):
    pass


def send_dbus_action(stream_id, action_name):
    screen_name = 'camera%d' % stream_id

    # wait for omxplayer to initialise
    done, retry = 0, 0
    while done == 0:
        try:
            dbus_if_player, dbus_if_props, dbus_if_root = open_dbus_attempt(screen_name)
            log.debug('\t[%s] - dbus connected for stream URL: [%s]' % (screen_name, dbus_if_props.GetSource()))
            action_function = actions.get(action_name)
            result = action_function(screen_name, dbus_if_player, dbus_if_props, dbus_if_root)
            done = 1
            return result
        except Exception as e:
            retry += 1
            time.sleep(DBUS_RETRY_INTERVAL)
            if retry >= 10:
                log.debug('\t[%s] - dbus connection FAILED: (%s)' % (screen_name, repr(e)))
                raise OMXPlayerStopError()


def open_dbus_attempt(screen_name):
    with open(DBUS_FILE_NAME_OMXPLAYER, 'r+') as f:
        omxplayer_dbus = f.read().strip()

    dbus_bus = dbus.bus.BusConnection(omxplayer_dbus)
    d_stream_id = 'org.mpris.MediaPlayer2.omxplayer.%s' % screen_name
    dbus_object = dbus_bus.get_object(d_stream_id, '/org/mpris/MediaPlayer2', introspect=False)
    dbus_if_props = dbus.Interface(dbus_object, 'org.freedesktop.DBus.Properties')
    dbus_if_player = dbus.Interface(dbus_object, 'org.mpris.MediaPlayer2.Player')
    dbus_if_root = dbus.Interface(dbus_object, 'org.mpris.MediaPlayer2')
    return dbus_if_player, dbus_if_props, dbus_if_root


if __name__ == '__main__':
    main()