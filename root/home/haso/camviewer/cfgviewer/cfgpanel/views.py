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

import re
import socket
import subprocess

from django.shortcuts import render

from config_utils import parse_interfaces_cfg, parse_cam_config, CAM_TYPE_HASO_KG1
from constants import CFG_PATH, ADMIN_PASS, ERR_MSG_DETAILS, ERR_MSG_VALIDATION, REGEX_IP_FORMAT, REQUIRED_FORMAT_IP_ADDRESS, REGEX_IP_ADDRESS, KEYWORD_ADDRESS, KEYWORD_NETMASK
from constants import CFG_SERIAL_FILENAME, CFG_MON_IP_FILENAME, DEFAULT_SERIAL, MON_ADDRESS_NOT_CONFIGURED, MON_NETMASK_NOT_CONFIGURED, CFG_CAM_IP_FILENAME
from utils import replace, btn_esc


def is_valid_ip(addr):
    try:
        socket.inet_aton(addr)
        return True
    except socket.error:
        return False


def index(request):
    # read current configuration value
    try:
        cfg_mon_file = open(CFG_PATH + CFG_MON_IP_FILENAME)
        str_mon = cfg_mon_file.read()

        current_mon_address, current_mon_netmask = parse_interfaces_cfg(str_mon)
    except IOError:
        current_mon_address, current_mon_netmask = MON_ADDRESS_NOT_CONFIGURED, MON_NETMASK_NOT_CONFIGURED

    cam_config_entry = parse_cam_config(CFG_PATH + CFG_CAM_IP_FILENAME)

    print 'Current config loaded.'

    current_cam_address1 = cam_config_entry[0].address
    current_cam_address2 = cam_config_entry[1].address
    current_cam_address3 = cam_config_entry[2].address
    current_cam_address4 = cam_config_entry[3].address

    current_cam_port1 = cam_config_entry[0].port
    current_cam_port2 = cam_config_entry[1].port
    current_cam_port3 = cam_config_entry[2].port
    current_cam_port4 = cam_config_entry[3].port

    current_cam_stream_m1 = cam_config_entry[0].stream_m
    current_cam_stream_m2 = cam_config_entry[1].stream_m
    current_cam_stream_m3 = cam_config_entry[2].stream_m
    current_cam_stream_m4 = cam_config_entry[3].stream_m

    current_cam_stream_s1 = cam_config_entry[0].stream_s
    current_cam_stream_s2 = cam_config_entry[1].stream_s
    current_cam_stream_s3 = cam_config_entry[2].stream_s
    current_cam_stream_s4 = cam_config_entry[3].stream_s

    current_cam_user1 = cam_config_entry[0].user
    current_cam_user2 = cam_config_entry[1].user
    current_cam_user3 = cam_config_entry[2].user
    current_cam_user4 = cam_config_entry[3].user

    current_cam_pass1 = cam_config_entry[0].password
    current_cam_pass2 = cam_config_entry[1].password
    current_cam_pass3 = cam_config_entry[2].password
    current_cam_pass4 = cam_config_entry[3].password

    current_cam_type1 = cam_config_entry[0].cam_type
    current_cam_type2 = cam_config_entry[1].cam_type
    current_cam_type3 = cam_config_entry[2].cam_type
    current_cam_type4 = cam_config_entry[3].cam_type

    print 'Current config data fetched.'

    # read new values from request and validate them (only if changed)

    new_mon_address = request.POST.get('new_mon_address', current_mon_address)
    new_mon_netmask = request.POST.get('new_mon_netmask', current_mon_netmask)

    new_cam_address1 = request.POST.get('new_cam_address1', current_cam_address1)
    new_cam_address2 = request.POST.get('new_cam_address2', current_cam_address2)
    new_cam_address3 = request.POST.get('new_cam_address3', current_cam_address3)
    new_cam_address4 = request.POST.get('new_cam_address4', current_cam_address4)

    new_cam_port1 = request.POST.get('new_cam_port1', current_cam_port1)
    new_cam_port2 = request.POST.get('new_cam_port2', current_cam_port2)
    new_cam_port3 = request.POST.get('new_cam_port3', current_cam_port3)
    new_cam_port4 = request.POST.get('new_cam_port4', current_cam_port4)

    new_cam_stream_m1 = request.POST.get('new_cam_stream_m1', current_cam_stream_m1)
    new_cam_stream_m2 = request.POST.get('new_cam_stream_m2', current_cam_stream_m2)
    new_cam_stream_m3 = request.POST.get('new_cam_stream_m3', current_cam_stream_m3)
    new_cam_stream_m4 = request.POST.get('new_cam_stream_m4', current_cam_stream_m4)

    new_cam_stream_s1 = request.POST.get('new_cam_stream_s1', current_cam_stream_s1)
    new_cam_stream_s2 = request.POST.get('new_cam_stream_s2', current_cam_stream_s2)
    new_cam_stream_s3 = request.POST.get('new_cam_stream_s3', current_cam_stream_s3)
    new_cam_stream_s4 = request.POST.get('new_cam_stream_s4', current_cam_stream_s4)

    new_cam_user1 = request.POST.get('new_cam_user1', current_cam_user1)
    new_cam_user2 = request.POST.get('new_cam_user2', current_cam_user2)
    new_cam_user3 = request.POST.get('new_cam_user3', current_cam_user3)
    new_cam_user4 = request.POST.get('new_cam_user4', current_cam_user4)

    new_cam_pass1 = request.POST.get('new_cam_pass1', current_cam_pass1)
    new_cam_pass2 = request.POST.get('new_cam_pass2', current_cam_pass2)
    new_cam_pass3 = request.POST.get('new_cam_pass3', current_cam_pass3)
    new_cam_pass4 = request.POST.get('new_cam_pass4', current_cam_pass4)

    new_cam_type1 = request.POST.get('new_cam_type1', current_cam_type1)
    new_cam_type2 = request.POST.get('new_cam_type2', current_cam_type2)
    new_cam_type3 = request.POST.get('new_cam_type3', current_cam_type3)
    new_cam_type4 = request.POST.get('new_cam_type4', current_cam_type4)

    new_serial_number = request.POST.get('new_serial_number', '')

    admin_password = request.POST.get('admin_password', '')
    if new_serial_number != '' and admin_password == ADMIN_PASS:
        with open(CFG_PATH + CFG_SERIAL_FILENAME, 'w+') as f:
            f.write(new_serial_number.strip())
        op_status = u'Zmieniono numer seryjny.'
    elif new_serial_number != '' and admin_password != ADMIN_PASS:
        op_status = u'Niepoprawne hasło serwisowe.'
    else:
        op_status = ''

    redirect_address = ''
    info_mon_address = ''
    info_mon_netmask = ''

    info_cam_data1 = ''
    info_cam_data2 = ''
    info_cam_data3 = ''
    info_cam_data4 = ''

    info_serial_number = ''

    change_mon_address = False
    change_mon_netmask = False
    change_cam_address = False
    reboot_needed = False

    if new_mon_address != current_mon_address:
        if re.match(REGEX_IP_ADDRESS, new_mon_address) and is_valid_ip(new_mon_address):
            change_mon_address = True
        else:
            info_mon_address = ERR_MSG_DETAILS % ('IP monitora', new_mon_address, REQUIRED_FORMAT_IP_ADDRESS)
            op_status = ERR_MSG_VALIDATION
    if new_mon_netmask != current_mon_netmask:
        if re.match(REGEX_IP_ADDRESS, new_mon_netmask) and is_valid_ip(new_mon_netmask):
            change_mon_netmask = True
        else:
            info_mon_netmask = ERR_MSG_DETAILS % ('Maska monitora', new_mon_address, REQUIRED_FORMAT_IP_ADDRESS)
            op_status = ERR_MSG_VALIDATION

    # cameras addresses
    if new_cam_address1 != current_cam_address1 \
            or new_cam_port1 != current_cam_port1 \
            or new_cam_stream_m1 != current_cam_stream_m1 \
            or new_cam_stream_s1 != current_cam_stream_s1 \
            or new_cam_user1 != current_cam_user1 \
            or new_cam_pass1 != current_cam_pass1 \
            or new_cam_type1 != current_cam_type1:

        if is_valid_ip_field_value(new_cam_address1):
            change_cam_address = True
        else:
            info_cam_data1 = ERR_MSG_DETAILS % ('IP kamery 1', new_cam_address1, REQUIRED_FORMAT_IP_ADDRESS)
            op_status = ERR_MSG_VALIDATION

    if new_cam_address2 != current_cam_address2 \
            or new_cam_port2 != current_cam_port2 \
            or new_cam_stream_m2 != current_cam_stream_m2 \
            or new_cam_stream_s2 != current_cam_stream_s2 \
            or new_cam_user2 != current_cam_user2 \
            or new_cam_pass2 != current_cam_pass2 \
            or new_cam_type2 != current_cam_type2:

        if is_valid_ip_field_value(new_cam_address2):
            change_cam_address = True
        else:
            info_cam_data2 = ERR_MSG_DETAILS % ('IP kamery 2', new_cam_address2, REQUIRED_FORMAT_IP_ADDRESS)
            op_status = ERR_MSG_VALIDATION

    if new_cam_address3 != current_cam_address3 \
            or new_cam_port3 != current_cam_port3 \
            or new_cam_stream_m3 != current_cam_stream_m3 \
            or new_cam_stream_s3 != current_cam_stream_s3 \
            or new_cam_user3 != current_cam_user3 \
            or new_cam_pass3 != current_cam_pass3 \
            or new_cam_type3 != current_cam_type3:

        if is_valid_ip_field_value(new_cam_address3):
            change_cam_address = True
        else:
            info_cam_data3 = ERR_MSG_DETAILS % ('IP kamery 3', new_cam_address3, REQUIRED_FORMAT_IP_ADDRESS)
            op_status = ERR_MSG_VALIDATION

    if new_cam_address4 != current_cam_address4 \
            or new_cam_port4 != current_cam_port4 \
            or new_cam_stream_m4 != current_cam_stream_m4 \
            or new_cam_stream_s4 != current_cam_stream_s4 \
            or new_cam_user4 != current_cam_user4 \
            or new_cam_pass4 != current_cam_pass4 \
            or new_cam_type4 != current_cam_type4:

        if is_valid_ip_field_value(new_cam_address4):
            change_cam_address = True
        else:
            info_cam_data4 = ERR_MSG_DETAILS % ('IP kamery 4', new_cam_address4, REQUIRED_FORMAT_IP_ADDRESS)
            op_status = ERR_MSG_VALIDATION

    # update current values
    if op_status == '':
        print 'Checking current values...'
        if change_mon_address:
            replace(CFG_PATH + CFG_MON_IP_FILENAME, r'%s %s' % (KEYWORD_ADDRESS, REGEX_IP_FORMAT), KEYWORD_ADDRESS + ' ' + new_mon_address.strip())
            reboot_needed = True
            redirect_address = new_mon_address  # after reboot user should be redirected to the new address he set
            new_mon_address = ''

        if change_mon_netmask:
            replace(CFG_PATH + CFG_MON_IP_FILENAME, r'%s %s' % (KEYWORD_NETMASK, REGEX_IP_FORMAT), KEYWORD_NETMASK + ' ' + new_mon_netmask.strip())
            reboot_needed = True
            new_mon_netmask = ''

        if change_cam_address:
            with open(CFG_PATH + CFG_CAM_IP_FILENAME, 'w+') as f:
                f.write('%s|%s|%s|%s|%s|%s|%s\n' % (
                    new_cam_address1.strip(), port_check(new_cam_port1), new_cam_stream_m1.strip(), new_cam_stream_s1.strip(), new_cam_user1.strip(), new_cam_pass1.strip(), new_cam_type1.strip()))
                f.write('%s|%s|%s|%s|%s|%s|%s\n' % (
                    new_cam_address2.strip(), port_check(new_cam_port2), new_cam_stream_m2.strip(), new_cam_stream_s2.strip(), new_cam_user2.strip(), new_cam_pass2.strip(), new_cam_type2.strip()))
                f.write('%s|%s|%s|%s|%s|%s|%s\n' % (
                    new_cam_address3.strip(), port_check(new_cam_port3), new_cam_stream_m3.strip(), new_cam_stream_s3.strip(), new_cam_user3.strip(), new_cam_pass3.strip(), new_cam_type3.strip()))
                f.write('%s|%s|%s|%s|%s|%s|%s\n' % (
                    new_cam_address4.strip(), port_check(new_cam_port4), new_cam_stream_m4.strip(), new_cam_stream_s4.strip(), new_cam_user4.strip(), new_cam_pass4.strip(), new_cam_type4.strip()))
                f.close()

            new_cam_address1 = ''
            new_cam_address2 = ''
            new_cam_address3 = ''
            new_cam_address4 = ''

            new_cam_port1 = ''
            new_cam_port2 = ''
            new_cam_port3 = ''
            new_cam_port4 = ''

            new_cam_stream_m1 = ''
            new_cam_stream_m2 = ''
            new_cam_stream_m3 = ''
            new_cam_stream_m4 = ''
            
            new_cam_stream_s1 = ''
            new_cam_stream_s2 = ''
            new_cam_stream_s3 = ''
            new_cam_stream_s4 = ''

            new_cam_user1 = ''
            new_cam_user2 = ''
            new_cam_user3 = ''
            new_cam_user4 = ''

            new_cam_pass1 = ''
            new_cam_pass2 = ''
            new_cam_pass3 = ''
            new_cam_pass4 = ''

            new_cam_type1 = CAM_TYPE_HASO_KG1
            new_cam_type2 = CAM_TYPE_HASO_KG1
            new_cam_type3 = CAM_TYPE_HASO_KG1
            new_cam_type4 = CAM_TYPE_HASO_KG1

            btn_esc()  # emulates ESC button pressed - exits from streaming to configuration view

    # read new values and send to view
    try:
        cfg_mon_file = open(CFG_PATH + CFG_MON_IP_FILENAME)
        str_mon = cfg_mon_file.read()
        current_mon_address, current_mon_netmask = parse_interfaces_cfg(str_mon)
        print 'New monitor config values: (%s) (%s)' % (current_mon_address, current_mon_netmask)
    except IOError:
        current_mon_address, current_mon_netmask = MON_ADDRESS_NOT_CONFIGURED, MON_NETMASK_NOT_CONFIGURED

    cam_config_entry = parse_cam_config(CFG_PATH + CFG_CAM_IP_FILENAME)

    print 'New config loaded.'

    current_cam_address1 = cam_config_entry[0].address
    current_cam_address2 = cam_config_entry[1].address
    current_cam_address3 = cam_config_entry[2].address
    current_cam_address4 = cam_config_entry[3].address

    current_cam_port1 = cam_config_entry[0].port
    current_cam_port2 = cam_config_entry[1].port
    current_cam_port3 = cam_config_entry[2].port
    current_cam_port4 = cam_config_entry[3].port

    current_cam_stream_m1 = cam_config_entry[0].stream_m
    current_cam_stream_m2 = cam_config_entry[1].stream_m
    current_cam_stream_m3 = cam_config_entry[2].stream_m
    current_cam_stream_m4 = cam_config_entry[3].stream_m

    current_cam_stream_s1 = cam_config_entry[0].stream_s
    current_cam_stream_s2 = cam_config_entry[1].stream_s
    current_cam_stream_s3 = cam_config_entry[2].stream_s
    current_cam_stream_s4 = cam_config_entry[3].stream_s

    current_cam_user1 = cam_config_entry[0].user
    current_cam_user2 = cam_config_entry[1].user
    current_cam_user3 = cam_config_entry[2].user
    current_cam_user4 = cam_config_entry[3].user

    current_cam_pass1 = cam_config_entry[0].password
    current_cam_pass2 = cam_config_entry[1].password
    current_cam_pass3 = cam_config_entry[2].password
    current_cam_pass4 = cam_config_entry[3].password

    current_cam_type1 = cam_config_entry[0].cam_type
    current_cam_type2 = cam_config_entry[1].cam_type
    current_cam_type3 = cam_config_entry[2].cam_type
    current_cam_type4 = cam_config_entry[3].cam_type

    print 'New config data fetched.'

    try:
        cfg_serial_file = open(CFG_PATH + CFG_SERIAL_FILENAME)
        current_serial_number = cfg_serial_file.read()
    except IOError:
        current_serial_number = DEFAULT_SERIAL

    # return to same page to set new values or display message
    context = {
        'current_mon_address': current_mon_address.strip(),
        'current_mon_netmask': current_mon_netmask.strip(),

        'current_cam_address1': current_cam_address1.strip(),
        'current_cam_address2': current_cam_address2.strip(),
        'current_cam_address3': current_cam_address3.strip(),
        'current_cam_address4': current_cam_address4.strip(),
        
        'current_cam_port1': current_cam_port1.strip(),
        'current_cam_port2': current_cam_port2.strip(),
        'current_cam_port3': current_cam_port3.strip(),
        'current_cam_port4': current_cam_port4.strip(),
        
        'current_cam_stream_m1': current_cam_stream_m1.strip(),
        'current_cam_stream_m2': current_cam_stream_m2.strip(),
        'current_cam_stream_m3': current_cam_stream_m3.strip(),
        'current_cam_stream_m4': current_cam_stream_m4.strip(),
        
        'current_cam_stream_s1': current_cam_stream_s1.strip(),
        'current_cam_stream_s2': current_cam_stream_s2.strip(),
        'current_cam_stream_s3': current_cam_stream_s3.strip(),
        'current_cam_stream_s4': current_cam_stream_s4.strip(),
        
        'current_cam_user1': current_cam_user1.strip(),
        'current_cam_user2': current_cam_user2.strip(),
        'current_cam_user3': current_cam_user3.strip(),
        'current_cam_user4': current_cam_user4.strip(),
        
        'current_cam_pass1': current_cam_pass1.strip(),
        'current_cam_pass2': current_cam_pass2.strip(),
        'current_cam_pass3': current_cam_pass3.strip(),
        'current_cam_pass4': current_cam_pass4.strip(),
        
        'current_cam_type1': current_cam_type1.strip(),
        'current_cam_type2': current_cam_type2.strip(),
        'current_cam_type3': current_cam_type3.strip(),
        'current_cam_type4': current_cam_type4.strip(),
        
        'current_serial_number': current_serial_number.strip(),
        'new_mon_address': new_mon_address.strip(),
        'new_mon_netmask': new_mon_netmask.strip(),

        'new_cam_address1': new_cam_address1.strip(),
        'new_cam_address2': new_cam_address2.strip(),
        'new_cam_address3': new_cam_address3.strip(),
        'new_cam_address4': new_cam_address4.strip(),

        'new_cam_port1': new_cam_port1.strip(),
        'new_cam_port2': new_cam_port2.strip(),
        'new_cam_port3': new_cam_port3.strip(),
        'new_cam_port4': new_cam_port4.strip(),

        'new_cam_stream_m1': new_cam_stream_m1.strip(),
        'new_cam_stream_m2': new_cam_stream_m2.strip(),
        'new_cam_stream_m3': new_cam_stream_m3.strip(),
        'new_cam_stream_m4': new_cam_stream_m4.strip(),
        
        'new_cam_stream_s1': new_cam_stream_s1.strip(),
        'new_cam_stream_s2': new_cam_stream_s2.strip(),
        'new_cam_stream_s3': new_cam_stream_s3.strip(),
        'new_cam_stream_s4': new_cam_stream_s4.strip(),

        'new_cam_user1': new_cam_user1.strip(),
        'new_cam_user2': new_cam_user2.strip(),
        'new_cam_user3': new_cam_user3.strip(),
        'new_cam_user4': new_cam_user4.strip(),

        'new_cam_pass1': new_cam_pass1.strip(),
        'new_cam_pass2': new_cam_pass2.strip(),
        'new_cam_pass3': new_cam_pass3.strip(),
        'new_cam_pass4': new_cam_pass4.strip(),

        'new_cam_type1': new_cam_type1.strip(),
        'new_cam_type2': new_cam_type2.strip(),
        'new_cam_type3': new_cam_type3.strip(),
        'new_cam_type4': new_cam_type4.strip(),

        'info_mon_address': info_mon_address.strip(),
        'info_mon_netmask': info_mon_netmask.strip(),

        'info_cam_data1': info_cam_data1.strip(),
        'info_cam_data2': info_cam_data2.strip(),
        'info_cam_data3': info_cam_data3.strip(),
        'info_cam_data4': info_cam_data4.strip(),

        'info_serial_number': info_serial_number.strip(),
        'redirect_address': redirect_address,
        'op_status': op_status,
    }
    if reboot_needed:
        print 'Reboot required..'
        # Network interfaces and then cfgviewer server itself need to be reboot
        subprocess.call(['bash', 'reboot.sh'])  # should fire after some delay and go asynchronously
        return render(request, 'cfgpanel/reboot.html', context)
        pass

    return render(request, 'cfgpanel/index.html', context)


def port_check(port_val):
    port_val = port_val.strip()
    return port_val if port_val is not None and len(port_val) > 0 else 554


def is_valid_ip_field_value(address_value):
    if address_value == '':
        return True

    return re.match(REGEX_IP_ADDRESS, address_value) and is_valid_ip(address_value)


def service_input(request):
    mac_address = 'nieustalony'
    try:
        get_mac_cmd = "ifconfig | grep eth0:0 | awk '{print $5}'"
        sys_cmd_process = subprocess.Popen([get_mac_cmd], stdout=subprocess.PIPE, shell=True)
        (mac_address, err) = sys_cmd_process.communicate()
        if err:
            print 'ERROR while getting MAC address (%s).' % err
    except BaseException:
        pass
    print 'MAC address: (%s).' % mac_address

    context = {
        'mac_address': str(mac_address).strip()
    }
    return render(request, 'cfgpanel/service_input.html', context)
