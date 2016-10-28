#!/usr/bin/env python
import os
import time
# noinspection PyUnresolvedReferences
import dbus

DBUS_FILE_NAME_OMXPLAYER = '/tmp/omxplayerdbus.%s' % os.getlogin()


def main():
    send_dbus_stop()


class OMXPlayerStopError(BaseException):
    pass


def send_dbus_stop():
    # wait for omxplayer to initialise
    done, retry = 0, 0
    while done == 0:
        try:
            with open(DBUS_FILE_NAME_OMXPLAYER, 'r+') as f:
                omxplayer_dbus = f.read().strip()

            dbus_bus = dbus.bus.BusConnection(omxplayer_dbus)
            dbus_object = dbus_bus.get_object('org.mpris.MediaPlayer2.omxplayer', '/org/mpris/MediaPlayer2', introspect=False)
            dbus_if_props = dbus.Interface(dbus_object, 'org.freedesktop.DBus.Properties')
            dbus_if_player = dbus.Interface(dbus_object, 'org.mpris.MediaPlayer2.Player')
            done = 1
            print "OK"

            print dbus_if_props.Duration()
            print dbus_if_props.GetSource()
            dbus_if_player.Stop()

        except Exception as e:
            retry += 1
            time.sleep(0.2)

            if retry >= 10:
                print "ERROR while opening DBUS (%s)" % e
                raise OMXPlayerStopError()


if __name__ == '__main__':
    main()
