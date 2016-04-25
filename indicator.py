#!/usr/bin/env python3

import os
import signal
import subprocess

from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator

APPINDICATOR_ID = 'au.com.knightcode.brightness'

def main():
    print("Icons designed by Freepik")
    icon_dark   = os.path.abspath('dark.svg')
    icon_dim    = os.path.abspath('dim.svg')
    icon_bright = os.path.abspath('bright.svg')

    # Handle signals properly.
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Build the menu.
    menu = gtk.Menu()

    num_steps = 10
    for step in range(num_steps, -1, -1):
        level = step/float(num_steps)
        level_pc = round(level * 100)
        item_brightness = gtk.MenuItem(str(level_pc) + '%')
        item_brightness.brightness_level = level
        item_brightness.connect('activate', ev_set_brightness)
        menu.append(item_brightness)
    menu.append(gtk.SeparatorMenuItem())

    item_quit = gtk.MenuItem('Quit')
    item_quit.connect('activate', ev_quit)
    menu.append(item_quit)
    
    menu.show_all()

    # Create the indicator
    indicator = appindicator.Indicator.new(APPINDICATOR_ID, icon_dim, appindicator.IndicatorCategory.SYSTEM_SERVICES)
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_menu(menu)

    # Start the GTK loop.
    gtk.main()

def ev_quit(source):
    """Stop everythin. For when the user wants to quit."""
    gtk.main_quit()

def ev_set_brightness(source):
    set_brightness(source.brightness_level)


def set_brightness(level):
    subprocess.call(['xrandr', '--output', 'eDP1', '--brightness', str(level)])

if __name__ == "__main__":
    main()
