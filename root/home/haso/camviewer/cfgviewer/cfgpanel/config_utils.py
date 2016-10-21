import os
import string

from constants import *


class ConfigEntry(object):
    address = ''
    port = ''
    stream_m = ''
    stream_s = ''
    user = ''
    password = ''
    cam_type = ''

    def __str__(self):
        return self.main_stream_url()

    def info(self):
        if self.user:
            auth = '%s:%s @ ' % (self.user, '***' if self.password else '')
        else:
            auth = ''

        if self.cam_type == 'haso':
            streams = ' '
            type_desc = 'typ: HASO KG-1'
        elif self.cam_type == 'samsung':
            streams = ' profil: %s/%s ' % (self.stream_m, self.stream_s)
            type_desc = 'typ: Samsung SNZ-5200'
        else:
            streams = ' profil: %s/%s ' % (self.stream_m, self.stream_s)
            type_desc = 'typ: nieznany'

        port = 'port: %s' % self.port
        return '[%s%s%s%s]' % (auth, port, streams, type_desc)

    def main_stream_url(self):
        if self.cam_type == 'haso':
            if self.user:
                return 'rtsp://%s:%s/av0_0&user=%s&password=%s' % (self.address, self.port, self.user, self.password)
            else:
                return 'rtsp://%s:%s/av0_0' % (self.address, self.port)
        else:
            if self.user:
                return 'rtsp://%s:%s@%s:%s/profile%s/media.smp' % (self.user, self.password, self.address, self.port, self.stream_m)
            else:
                return 'rtsp://%s:%s/profile%s/media.smp' % (self.address, self.port, self.stream_m)

    def sub_stream_url(self):
        if self.cam_type == 'haso':
            if self.user:
                return 'rtsp://%s:%s/av0_1&user=%s&password=%s' % (self.address, self.port, self.user, self.password)
            else:
                return 'rtsp://%s:%s/av0_1' % (self.address, self.port)
        else:
            if self.user:
                return 'rtsp://%s:%s@%s:%s/profile%s/media.smp' % (self.user, self.password, self.address, self.port, self.stream_s)
            else:
                return 'rtsp://%s:%s/profile%s/media.smp' % (self.address, self.port, self.stream_s)


def parse_interfaces_cfg(str_mon):
    cfg_mon_str = string.split(str_mon, '\n')
    cfg_address = "N/A"
    cfg_netmask = "N/A"

    for str_cfg_part in cfg_mon_str:
        if str_cfg_part.find(KEYWORD_ADDRESS) == 0:
            cfg_address = str_cfg_part[7:].strip()
        elif str_cfg_part.find(KEYWORD_NETMASK) == 0:
            cfg_netmask = str_cfg_part[7:].strip()

    return cfg_address, cfg_netmask


def parse_cam_config(cam_cfg_path):
    print 'Loading cameras config...'
    print os.system('pwd')

    current_config_string = EMPTY_CONFIG_CONTENT
    try:
        with open(cam_cfg_path) as f:
            current_config_string = f.read()
            f.close()
    except IOError as ioe:
        print('Could not open (%s) file. (%s)' % (cam_cfg_path, repr(ioe)))

    cam_config = [(ConfigEntry()), (ConfigEntry()), (ConfigEntry()), (ConfigEntry())]
    config_lines = string.split(current_config_string, '\n')
    for i in range(0, MAX_CAM_AMOUNT):
        if config_lines[i]:
            params = string.split(config_lines[i], '|')
            cfg_entry = cam_config[i]

            cfg_entry.address = params[0]
            cfg_entry.port = params[1]
            cfg_entry.stream_m = params[2]
            cfg_entry.stream_s = params[3]
            cfg_entry.user = params[4]
            cfg_entry.password = params[5]
            cfg_entry.cam_type = params[6]

    for i in range(0, MAX_CAM_AMOUNT):
        print 'Loaded: %s' % str(cam_config[i])

    return cam_config
