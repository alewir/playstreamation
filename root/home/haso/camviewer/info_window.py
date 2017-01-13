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

import _tkinter
import tkFont
from Tkconstants import BOTTOM, TOP, X, E, SUNKEN, LEFT, RIGHT, Y
from Tkinter import Tk, Frame, Label, BOTH, StringVar

from PIL import Image, ImageTk

from cfgviewer.cfgpanel.constants import MAX_CAM_AMOUNT, CAM_STATUS_INIT
from log_config import log
from utils import MODE_SPLIT, MODE_AUTO, SCREEN_RES, APP_LOGO_PNG, APP_HELP_S_PNG, APP_HELP_A_PNG, APP_HELP_4_PNG, MODE_SINGLE

BORDER_WIDTH = 3
DEF_RELIEF = SUNKEN
DEF_FONT = "Helvetica"
MONO_FONT = "Courier"
FRM_BACKGROUND = "#AAAAAA"
MSG_BACKGROUND = "#BBBBBB"
MSG_TITLE_FOREGROUND = "#0B2161"
MSG_HELP_FOREGROUND = "#015f94"
SEP_L = "------------------------------------"

TXT_UPDATE_INTERVAL = 400  # ms
PING_DELAY = 3  # s

try:
    TK_ROOT = Tk()
    TK_ROOT.geometry("%s+0+0" % SCREEN_RES)
except _tkinter.TclError:
    print 'ERROR: This application requires X window server.'
    exit(-1)


class SysInfo(Frame):
    txt_var_serial = StringVar()
    txt_var_mon_cfg = StringVar()
    txt_var_cam_cfg_page = StringVar()
    txt_var_cam_cfg_stream = StringVar()
    txt_var_version = StringVar()
    txt_var_mode_name = StringVar()

    img_help_single = ImageTk.PhotoImage(Image.open(APP_HELP_S_PNG))
    img_help_auto = ImageTk.PhotoImage(Image.open(APP_HELP_A_PNG))
    img_help_4in1 = ImageTk.PhotoImage(Image.open(APP_HELP_4_PNG))

    def __init__(self, parent, info_collector_thread):
        Frame.__init__(self, parent, background=FRM_BACKGROUND)

        # load images
        img_logo = ImageTk.PhotoImage(Image.open(APP_LOGO_PNG))

        # init frame
        self.parent = parent
        self.parent.title("MyFrame")
        self.info_collector = info_collector_thread

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        font_huge = tkFont.Font(family=DEF_FONT, size=36, weight="bold")
        font_mono = tkFont.Font(family=MONO_FONT, size=11)
        font_normal = tkFont.Font(family=DEF_FONT, size=14)
        font_normal_bold = tkFont.Font(family=DEF_FONT, size=16, weight="bold")
        font_small = tkFont.Font(family=DEF_FONT, size=10, weight="bold")
        font_tiny = tkFont.Font(family=DEF_FONT, size=10)

        frm_main = Frame(self, relief=DEF_RELIEF, background=MSG_BACKGROUND)
        frm_main.pack(side=BOTTOM, fill=BOTH, expand=True, padx=10, pady=10)

        frm_title = Frame(self, background=FRM_BACKGROUND)
        frm_title.pack(side=TOP, fill=X)

        frm_name = Frame(frm_title, background=FRM_BACKGROUND)
        frm_name.pack(side=RIGHT)

        frm_logo = Frame(frm_title, background=FRM_BACKGROUND)
        frm_logo.pack(side=LEFT)

        lbl_logo = Label(frm_logo, image=img_logo, background=FRM_BACKGROUND, relief=DEF_RELIEF, borderwidth=BORDER_WIDTH)
        lbl_logo.image = img_logo
        lbl_logo.pack(padx=10, pady=10)

        # TITLE

        lbl_name = Label(frm_name, text="Monitor górniczy MG-1", background=FRM_BACKGROUND, foreground=MSG_TITLE_FOREGROUND, font=font_huge)
        lbl_name.pack(padx=10, pady=10, anchor=E)

        lbl_serial = Label(frm_name, textvariable=self.txt_var_serial, background=FRM_BACKGROUND, foreground=MSG_HELP_FOREGROUND, font=font_normal_bold)
        lbl_serial.pack(padx=10, pady=10, anchor=E)

        # HELP

        frm_help = Frame(frm_main, borderwidth=0)
        frm_help.pack(side=LEFT, fill=Y)

        self.lbl_help = Label(frm_help, image=self.img_help_4in1, background=FRM_BACKGROUND, relief=DEF_RELIEF, borderwidth=BORDER_WIDTH)
        self.lbl_help.image = self.img_help_4in1  # default
        self.lbl_help.pack(fill=Y, expand=True)

        # CFG MESSAGE

        frm_sysinfo = Frame(frm_main, relief=DEF_RELIEF, background=MSG_BACKGROUND, borderwidth=BORDER_WIDTH)
        frm_sysinfo.pack(side=RIGHT, fill=BOTH, expand=True)

        frm_vertical_sep = Label(frm_main, background=FRM_BACKGROUND, borderwidth=0, width=1)
        frm_vertical_sep.pack(side=RIGHT, fill=BOTH)

        lbl_empty = Label(frm_sysinfo, text="", background=MSG_BACKGROUND)
        lbl_empty.pack(fill=X, expand=True)

        lbl_mon_cfg_title = Label(frm_sysinfo, text="Adres IP monitora", background=MSG_BACKGROUND, foreground=MSG_TITLE_FOREGROUND, font=font_normal)
        lbl_mon_cfg_title.pack(fill=X)
        lbl_mon_cfg = Label(frm_sysinfo, textvariable=self.txt_var_mon_cfg, background=MSG_BACKGROUND, font=font_normal)
        lbl_mon_cfg.pack(fill=X)

        lbl_empty = Label(frm_sysinfo, text="", background=MSG_BACKGROUND)
        lbl_empty.pack(fill=X, expand=True)

        lbl_cam_cfg_title = Label(frm_sysinfo, text="Adresy IP kamer", background=MSG_BACKGROUND, foreground=MSG_TITLE_FOREGROUND, font=font_normal)
        lbl_cam_cfg_title.pack(fill=X)
        lbl_cam_cfg_page = Label(frm_sysinfo, textvariable=self.txt_var_cam_cfg_page, background=MSG_BACKGROUND, font=font_normal)
        lbl_cam_cfg_page.pack(fill=X)
        lbl_cam_cfg_stream = Label(frm_sysinfo, textvariable=self.txt_var_cam_cfg_stream, background=MSG_BACKGROUND, font=font_mono, justify=LEFT)
        lbl_cam_cfg_stream.pack(fill=X)

        lbl_empty = Label(frm_sysinfo, text="", background=MSG_BACKGROUND, font=font_small)
        lbl_empty.pack(fill=X, expand=True)

        lbl_misc_title = Label(frm_sysinfo, text="Informacje dodatkowe", background=MSG_BACKGROUND, foreground=MSG_TITLE_FOREGROUND, font=font_small)
        lbl_misc_title.pack(fill=X)
        lbl_mode = Label(frm_sysinfo, textvariable=self.txt_var_mode_name, background=MSG_BACKGROUND, font=font_tiny)
        lbl_mode.pack(fill=X)
        self.txt_var_mode_name.set("<TRYB>")
        lbl_version = Label(frm_sysinfo, textvariable=self.txt_var_version, background=MSG_BACKGROUND, font=font_tiny)
        lbl_version.pack(fill=X)

        # pack main content panel
        self.pack(fill=BOTH, expand=True)

        self.after(TXT_UPDATE_INTERVAL, self.on_timer)

    def on_timer(self):
        log.debug("View update.")
        try:
            self.update_view()
        except BaseException as e:
            log.error('Could not update view (%s).' % repr(e))

        if self.info_collector.is_enabled:
            self.after(TXT_UPDATE_INTERVAL, self.on_timer)

    def update_view(self):
        info_serial = "Numer seryjny: %s" % self.info_collector.cfg_serial
        self.txt_var_serial.set(info_serial)

        str_mon_info = self.info_collector.cfg_address_mon + "\n" + self.info_collector.cfg_netmask_mon

        self.txt_var_mon_cfg.set(str_mon_info)
        config_info = "[odwiedź %s:8080/config/ aby zmienić]" % self.info_collector.cfg_address_mon

        cams_configs = self.info_collector.cams_configs
        cams_statuses = self.info_collector.cams_statuses
        cam_status = ''
        for i in range(0, MAX_CAM_AMOUNT):
            cam_config = cams_configs[i]
            address = cam_config.address
            port, type_name, auth, profiles = cam_config.cfg_info()
            status = cams_statuses[i]
            cam_address = '- nie skonfigurowano -' if not address and status != CAM_STATUS_INIT else address.rjust(15, ' ')
            if address:
                cam_status += 'kam:%s %s poł:%s port:%s %s %s %s\n' % ((i + 1), cam_address, status, port, type_name.ljust(17, ' '), auth, profiles)
            else:
                cam_status += 'kam:%s %s %s\n' % ((i + 1), cam_address.rjust(15, ' '), status)

        self.txt_var_cam_cfg_page.set("%s\n\n" % config_info)
        self.txt_var_cam_cfg_stream.set("%s" % cam_status.rstrip('\n'))
        self.txt_var_version.set("Wersja: %s.%s" % (self.info_collector.cfg_version, self.info_collector.cfg_revision))

        log.debug("Labels updated.")
        # print subprocess.check_output(['scrot', '-d', '3'])  # FOR DOCUMENTATION PURPOSE ONLY

    def set_mode_name(self, mode, mode_description):
        self.txt_var_mode_name.set("Tryb: %s" % mode_description)
        if mode == MODE_SPLIT:
            self.lbl_help.configure(image=self.img_help_4in1)
        elif mode == MODE_SINGLE:
            self.lbl_help.configure(image=self.img_help_single)
        elif mode == MODE_AUTO:
            self.lbl_help.configure(image=self.img_help_auto)


def create(info_collector_thread):
    return SysInfo(TK_ROOT, info_collector_thread)


def show():
    TK_ROOT.update()
    TK_ROOT.deiconify()
    TK_ROOT.mainloop()


def close():
    try:
        TK_ROOT.withdraw()
    except RuntimeError:
        print 'ERROR: Could not withdraw...'

    TK_ROOT.quit()


def finish():
    TK_ROOT.destroy()

