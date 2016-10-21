#!/usr/bin/env python
from cfgviewer.cfgpanel.constants import PIN_ENTER, PIN_ESC, PIN_UP, PIN_DOWN, PIN_LEFT, PIN_RIGHT
from cfgviewer.cfgpanel.utils import btn_enter, btn_esc, btn_up, btn_down, btn_left, btn_right

# noinspection PyUnresolvedReferences
from gpiozero import Button
# noinspection PyUnresolvedReferences
from signal import pause


def main():
    button_enter = Button(PIN_ENTER)
    button_enter.when_pressed = btn_enter

    button_esc = Button(PIN_ESC)
    button_esc.when_pressed = btn_esc

    button_up = Button(PIN_UP)
    button_up.when_pressed = btn_up

    button_down = Button(PIN_DOWN)
    button_down.when_pressed = btn_down

    button_left = Button(PIN_LEFT)
    button_left.when_pressed = btn_left

    button_right = Button(PIN_RIGHT)
    button_right.when_pressed = btn_right

    pause()


if __name__ == "__main__":
    main()
