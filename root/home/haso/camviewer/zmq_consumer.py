#!/usr/bin/env python

import zmq

from cfgviewer.cfgpanel.constants import ZMQ_PORT
from log_config import log


class ZmqConsumer:
    handle_event = None
    is_enabled = True

    def __init__(self, event_handler_method):
        self.handle_event = event_handler_method

        # ZeroMQ Server connection (Consumer)
        port = ZMQ_PORT
        context = zmq.Context()

        self.socket = context.socket(zmq.REP)
        self.socket.bind("tcp://*:%s" % port)
        self.mainloop()

    def mainloop(self):
        while self.is_enabled:
            try:
                msg = self.socket.recv()
                log.info('Message found in ZMQ: (%s)' % msg)

                if self.handle_event is not None:
                    print 'Invoking event handler...'
                    self.handle_event(msg)
                else:
                    print 'No handler registered for events...'

                self.socket.send("Finished processing: %s" % msg)
                log.info('Message handling finished for: (%s)' % msg)
            except KeyboardInterrupt:
                log.info('\nKeyboard interrupt intercepted - exiting...')
                break

        log.info('Exiting ZMQ consumer mainloop.')

    def disable(self):
        self.is_enabled = False


if __name__ == '__main__':
    ZmqConsumer(None)
