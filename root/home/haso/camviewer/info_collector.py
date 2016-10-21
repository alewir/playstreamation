# coding=utf-8
import subprocess
import threading
import time

import pyping

from cfgviewer.cfgpanel.config_utils import parse_interfaces_cfg, parse_cam_config, ConfigEntry
from cfgviewer.cfgpanel.constants import CAM_STATUS_INIT, CAM_STATUS_UNDEFINED, CAM_STATUS_OK, CAM_STATUS_NOT_CONNECTED
from cfgviewer.cfgpanel.utils import *
from info_window import log, PING_DELAY


def ping(cam_address):
    try:
        log.debug('Pinging camera with IP = (%s)' % cam_address)
        ping_resp = pyping.ping(cam_address)
        ping_status = ping_resp.ret_code
        log.debug('Ping return code for %s = %d' % (cam_address, ping_status))

        if ping_status == 0:
            return CAM_STATUS_OK
        else:
            return CAM_STATUS_NOT_CONNECTED
    except BaseException as e:
        log.error('PYPING library error: (%s)' % e.message)
    return CAM_STATUS_CON_ERROR


def fetch_version():
    try:
        log.debug('Opening software version file: %r.' % CFG_VERSION_FILENAME)
        with open(CFG_VERSION_FILENAME) as version_file:
            version_cfg_content = version_file.read().strip()
            version_file.close()
            return version_cfg_content
    except IOError:
        log.debug('Camera IP config file not found...')
    return DEFAULT_VERSION


def fetch_cfg_mon():
    try:
        log.debug('Opening monitor IP config file: %r.' % CFG_MON_IP_FILENAME)
        with open(CFG_MON_IP_FILENAME) as cfg_mon_file:
            str_mon_cfg = cfg_mon_file.read().strip()
            interface_cfg_content = parse_interfaces_cfg(str_mon_cfg)
            cfg_mon_file.close()
            return interface_cfg_content
    except IOError:
        log.error('Monitor IP config file not found...')
    return MON_ADDRESS_NOT_CONFIGURED, MON_NETMASK_NOT_CONFIGURED


def fetch_serial_number():
    log.debug('Opening serial number config file: %r.' % CFG_SERIAL_FILENAME)
    try:
        with open(CFG_SERIAL_FILENAME) as cfg_serial_file:
            serial_cfg_content = cfg_serial_file.read().strip()
            cfg_serial_file.close()
            return serial_cfg_content
    except IOError:
        log.debug('Serial number config file not found...')
    return DEFAULT_SERIAL


class InfoCollectorThread(threading.Thread):
    cfg_version = 'N/A'
    cfg_revision = 'build_number'
    cfg_serial = 'N/A'
    cfg_address_mon = 'N/A'
    cfg_netmask_mon = 'N/A'

    is_enabled = True

    msg_output = 'ENTER = przejdź do podglądu widoku z kamery.'

    cams_configs = [ConfigEntry(), ConfigEntry(), ConfigEntry(), ConfigEntry()]
    cams_statuses = [CAM_STATUS_INIT, CAM_STATUS_INIT, CAM_STATUS_INIT, CAM_STATUS_INIT]

    def __init__(self):
        super(InfoCollectorThread, self).__init__()

        try:
            self.cfg_revision = subprocess.check_output("svnversion").rstrip('\n')
        except OSError:
            log.error('Could not get SVN revision...')

    def run(self):
        try:
            log.info('Entering StatusReaderThread...')

            fetch_serial_number()
            self.update_model()

            log.info('Exiting StatusReaderThread...')
        except KeyboardInterrupt:
            self.stop()
            exit(0)

    def update_model(self):
        log.info('Entering Ping method...')
        self.is_enabled = True

        while self.is_enabled:
            self.cfg_version = fetch_version()
            self.cfg_address_mon, self.cfg_netmask_mon = fetch_cfg_mon()
            self.cfg_serial = fetch_serial_number()

            self.fetch_cams_config()

            # wait a while before next data read
            time.sleep(PING_DELAY)

        # finish refreshing only after stop invoked...
        return

    def stop(self):
        self.is_enabled = False
        self.join(5)
        pass

    def fetch_cams_config(self):
        cam_config_entries = parse_cam_config(CFG_CAM_IP_FILENAME)

        for i in range(0, MAX_CAM_AMOUNT):
            cam_config_entry = cam_config_entries[i]
            cam_address = cam_config_entry.address
            if not cam_address:
                cam_status = CAM_STATUS_UNDEFINED
            else:
                cam_status = ping(cam_address)

            self.cams_configs[i] = cam_config_entry
            self.cams_statuses[i] = cam_status
            log.info('Camera[%d]: IP=(%s), STATUS=(%s)' % (i + 1, cam_address, cam_status))

    def is_any_cam(self):
        for i in range(0, MAX_CAM_AMOUNT):
            cam_address = self.cams_configs[i].address
            if cam_address:
                cam_status = self.cams_statuses[i]
                available = cam_status == CAM_STATUS_OK
                log.info("Cam[%d] status=(%s)" % (i, available))

                if available:
                    return True

        return False
