# coding=utf-8
ZMQ_PORT = '5555'

PIN_ENTER = 26
PIN_ESC = 17
PIN_UP = 14
PIN_DOWN = 15
PIN_LEFT = 19
PIN_RIGHT = 04

BTN_SIGNAL_ESC = 'ESC'
BTN_SIGNAL_ENTER = 'ENTER'
BTN_SIGNAL_LEFT = 'LEFT'
BTN_SIGNAL_RIGHT = 'RIGHT'
BTN_SIGNAL_UP = 'UP'
BTN_SIGNAL_DOWN = 'DOWN'

AUTO_CLOSE_TIME = 20
CYCLE_TIME_DEFAULT = 10
CYCLE_TIME_MAX_INCR = 3600

MAX_CAM_AMOUNT = 4

WIN_SINGLE = '0,0,1060,600'

WIN_0 = '0,0,528,298'
WIN_1 = '532,0,1060,298'
WIN_2 = '0,302,528,600'
WIN_3 = '532,302,1060,600'
WIN_ARR = [WIN_0, WIN_1, WIN_2, WIN_3]

KEYWORD_NETMASK = "netmask"
KEYWORD_ADDRESS = "address"

CFG_VERSION_FILENAME = "version.txt"
CFG_CAM_IP_FILENAME = "config_cam.cfg"
CFG_MON_IP_FILENAME = "config_mon.cfg"
CFG_SERIAL_FILENAME = "config_serial.cfg"

DEFAULT_SERIAL = "not defined"
DEFAULT_VERSION = 'X.X'

MON_ADDRESS_NOT_CONFIGURED = "not configured"
MON_NETMASK_NOT_CONFIGURED = "not configured"

EMPTY_CONFIG_CONTENT = '||||||\n||||||\n||||||\n||||||\n'

CFG_PATH = '../'
ADMIN_PASS = 'secret'

ERR_MSG_DETAILS = u'%s - invalid value (%s) - required format is: %s'
ERR_MSG_VALIDATION = u'There were validation errors. New configuration values were not saved.'

REGEX_IP_FORMAT = '\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
REQUIRED_FORMAT_IP_ADDRESS = '<0-255>.<0-255>.<0-255>.<0-255>'

REGEX_IP_ADDRESS = r'%s' % REGEX_IP_FORMAT
REGEX_MON_ADDRESS = r'%s%s' % (KEYWORD_ADDRESS, REGEX_IP_FORMAT)
REGEX_MON_NETMASK = r'%s%s' % (KEYWORD_NETMASK, REGEX_IP_FORMAT)

CAM_STATUS_INIT = 'initialization...'  # Default value
CAM_STATUS_UNDEFINED = ''  # used when address IP is not defined for camera
CAM_STATUS_OK = '(OK)'
CAM_STATUS_NOT_CONNECTED = '(no connection)'
CAM_STATUS_CON_ERROR = '(connection error)'

