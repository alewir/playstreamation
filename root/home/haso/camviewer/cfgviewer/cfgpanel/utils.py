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

import re

import zmq

from constants import *


# ZeroMQ Client connection (Producer)
btn_port = ZMQ_PORT
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect('tcp://localhost:%s' % btn_port)


def handle_signal(signal_name):
    try:
        socket.send(signal_name)
        print 'Sent req=%s' % signal_name
        rep = socket.recv()
        print "Received reply %s" % rep
    except zmq.error.ZMQError:
        print 'processing...'


def replace(input_file, pattern, subst):
    print 'Replacing (%s) to (%s) in (%s)' % (pattern, subst, input_file)
    try:
        # Read contents from file as a single string
        with open(input_file, 'r') as file_handle:
            file_string = file_handle.read()
            print 'Current mon config content: (%s)' % file_string
            file_handle.close()

        # Use RE package to allow for replacement (also allowing for (multiline) REGEX)
        file_string = (re.sub(pattern, subst, file_string))

        # Write contents to file.
        # Using mode 'w' truncates the file.
        with open(input_file, 'w') as file_handle:
            file_handle.write(file_string)
            print 'New mon config content: (%s)' % file_string
            file_handle.close()
    except BaseException as be:
        print 'ERROR: Could not replace file content (%s).' % repr(be)


def btn_enter():
    handle_signal(BTN_SIGNAL_ENTER)


def btn_esc():
    handle_signal(BTN_SIGNAL_ESC)


def btn_up():
    handle_signal(BTN_SIGNAL_UP)


def btn_down():
    handle_signal(BTN_SIGNAL_DOWN)


def btn_left():
    handle_signal(BTN_SIGNAL_LEFT)


def btn_right():
    handle_signal(BTN_SIGNAL_RIGHT)
