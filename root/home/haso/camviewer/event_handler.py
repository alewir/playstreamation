from threading import Thread

from log import log
from zmq_consumer import ZmqConsumer

BTN_NAME_ESC = 'ESC'
BTN_NAME_ENTER = 'ENTER'
BTN_NAME_UP = 'UP'
BTN_NAME_DOWN = 'DOWN'
BTN_NAME_LEFT = 'LEFT'
BTN_NAME_RIGHT = 'RIGHT'


class EventHandlerThread(Thread):
    event_consumer = None

    handle_esc = None
    handle_enter = None
    handle_up = None
    handle_down = None
    handle_left = None
    handle_right = None

    def __init__(self):
        super(EventHandlerThread, self).__init__()

    def handle_button(self, btn_name):
        if btn_name == BTN_NAME_ESC and self.handle_esc is not None:
            print 'Invoking ESC handler...'
            self.handle_esc()
        elif btn_name == BTN_NAME_ENTER and self.handle_enter is not None:
            print 'Invoking ENTER handler...'
            self.handle_enter()
        elif btn_name == BTN_NAME_UP and self.handle_up is not None:
            print 'Invoking UP handler...'
            self.handle_up()
        elif btn_name == BTN_NAME_DOWN and self.handle_down is not None:
            print 'Invoking DOWN handler...'
            self.handle_down()
        elif btn_name == BTN_NAME_LEFT and self.handle_left is not None:
            print 'Invoking LEFT handler...'
            self.handle_left()
        elif btn_name == BTN_NAME_RIGHT and self.handle_right is not None:
            print 'Invoking RIGHT handler...'
            self.handle_right()
        else:
            print 'Unknown button name (%s) received...' % btn_name
        pass

    def run(self):
        try:
            log.info('Entering EventHandlerThread...')

            self.event_consumer = ZmqConsumer(self.handle_button)

            log.info('Exiting EventHandlerThread...')
        except KeyboardInterrupt:
            self.stop()
            exit(0)

    def set_esc_handler(self, handler_method):
        self.handle_esc = handler_method

    def set_enter_handler(self, handler_method):
        self.handle_enter = handler_method

    def set_up_handler(self, handler_method):
        self.handle_up = handler_method

    def set_down_handler(self, handler_method):
        self.handle_down = handler_method

    def set_left_handler(self, handler_method):
        self.handle_left = handler_method

    def set_right_handler(self, handler_method):
        self.handle_right = handler_method

    def stop(self):
        if self.event_consumer is not None:
            self.event_consumer.disable()
        self.join(5)
