#!/usr/bin/env python3

# Icons from http://www.flaticon.com/free-icons/brightness_644

import os
import signal
import subprocess

from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator

APPINDICATOR_ID = 'au.com.knightcode.brightness'

class BrightnessIndicator:

    def __init__(self):
        self.indicator = None
        self.level = None # We don't know what it is. (We could probably find out...)
        
        self.icon_dark   = os.path.abspath('dark.svg')
        self.icon_dim    = os.path.abspath('dim.svg')
        self.icon_bright = os.path.abspath('bright.svg')

        # Handle signals properly.
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        # Build the menu.
        menu = gtk.Menu()

        num_steps = 5
        for level in range(num_steps):
            level = 1.0/pow(2, level)
            level_pc = round(level * 100)
            item_brightness = gtk.MenuItem(str(level_pc) + '%')
            item_brightness.brightness_level = level
            item_brightness.connect('activate', self.ev_set_brightness)
            menu.append(item_brightness)
        menu.append(gtk.SeparatorMenuItem())

        item_quit = gtk.MenuItem('Quit')
        item_quit.connect('activate', self.ev_quit)
        menu.append(item_quit)
        
        menu.show_all()

        # Create the indicator
        self.indicator= appindicator.Indicator.new(APPINDICATOR_ID, self.icon_bright, appindicator.IndicatorCategory.SYSTEM_SERVICES)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(menu)

    def show(self):
        print("Icons designed by Freepik")
        gtk.main()

    def ev_quit(self, source):
        """Stop everything. For when the user wants to quit."""
        gtk.main_quit()

    def ev_set_brightness(self, source):
        set_system_brightness(source.brightness_level)

        self.level = source.brightness_level
        self.update_icon()

    def update_icon(self):
        if self.indicator is not None and self.level is not None:
            if self.level >= 0.99:
                self.indicator.set_icon(self.icon_bright)
            elif self.level > 0.3:
                self.indicator.set_icon(self.icon_dim)
            else:
                self.indicator.set_icon(self.icon_dark)

def set_system_brightness(level):
    subprocess.call(['xrandr', '--output', 'eDP1', '--brightness', str(level)])

def main():
    BrightnessIndicator().show()

if __name__ == "__main__":
    main()
