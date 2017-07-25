#!/usr/bin/env python3

import os
import re
import signal
import subprocess
import sys

from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator


APPINDICATOR_ID = 'au.com.knightcode.brightness'
APP_NAME = 'Brightness Indicator'
APP_DESCRIPTION = 'Change display brightness from the notification area'
DESKTOP_FILE_TEMPLATE = """[Desktop Entry]
Name={name}
Comment={comment}
Exec={exec}
Type=Application
"""

RESOURCE_DIR = os.path.dirname(__file__)
APP_EXEC = os.path.abspath(__file__)
AUTOSTART_DIR = os.path.join(os.environ['HOME'], '.config/autostart/')
AUTOSTART_FILE = os.path.join(AUTOSTART_DIR, 'indicator-brightness.desktop')

BRIGHTNESS_STEPS = 5


def check_autostart():
    return os.path.exists(AUTOSTART_FILE)

def create_autostart():
    if check_autostart():
        return
    if not os.path.exists(AUTOSTART_DIR):
        os.makedirs(AUTOSTART_DIR)
    with open(AUTOSTART_FILE, "w") as file:     
        file.write(DESKTOP_FILE_TEMPLATE.format(
            name=APP_NAME,
            comment=APP_DESCRIPTION,
            exec=APP_EXEC,
            ))

def remove_autostart():
    if not check_autostart():
        return
    os.remove(AUTOSTART_FILE)


connected_device = re.compile('^([^ ]+) connected')
def get_connected_displays():
    lines = subprocess.check_output(['xrandr', '--query'], universal_newlines=True).splitlines()
    return [match.group(1) for match in (connected_device.match(line) for line in lines) if match]

def set_system_brightness(display, level):
    subprocess.call(['xrandr', '--output', display, '--brightness', str(level)])


class Display:
    def __init__(self, indicator, id):
        self.indicator = indicator
        self.id = id
        self.level = None # We don't know what it is. (We could probably find out...)

        self.menu_items = []
        title_item = gtk.MenuItem(id)
        title_item.set_sensitive(False)
        self.menu_items.append(title_item)
        for level in range(BRIGHTNESS_STEPS):
            level = 1.0/pow(2, level)
            level_pc = round(level * 100)
            item_brightness = gtk.ImageMenuItem(str(level_pc) + '%')
            item_brightness.brightness_level = level
            item_brightness.connect('activate', self.ev_set_brightness)
            self.menu_items.append(item_brightness)
        self.menu_items.append(gtk.SeparatorMenuItem())

    def prepend_to(self, menu):
        for item in reversed(self.menu_items):
            menu.prepend(item)

    def remove_from(self, menu):
        for item in self.menu_items:
            menu.remove(item)

    def destroy(self):
        """Destroy all menu iems."""
        for item in self.menu_items:
            item.destroy()
        del self.menu_items[:]

    def ev_set_brightness(self, source):
        set_system_brightness(self.id, source.brightness_level)

        self.level = source.brightness_level
        self.indicator.update_icon(self.level)


class BrightnessIndicator:

    def __init__(self):
        self.displays = {}

        self.indicator = None
        self.menu = None

        self.icon_dark   = os.path.abspath(os.path.join(RESOURCE_DIR, 'dark.svg'))
        self.icon_dim    = os.path.abspath(os.path.join(RESOURCE_DIR, 'dim.svg'))
        self.icon_bright = os.path.abspath(os.path.join(RESOURCE_DIR, 'bright.svg'))

        # Handle signals properly.
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        # Build the menu.
        self.menu = gtk.Menu()

        item_refresh = gtk.MenuItem('Detect Displays')
        item_refresh.connect('activate', self.ev_detect_displays)
        self.menu.append(item_refresh)

        item_autostart = gtk.CheckMenuItem('Run on Startup')
        item_autostart.connect('toggled', self.ev_toggle_autostart)
        item_autostart.set_active(check_autostart())
        self.menu.append(item_autostart)

        item_quit = gtk.MenuItem('Quit')
        item_quit.connect('activate', self.ev_quit)
        self.menu.append(item_quit)
        
        self.menu.show_all()

        # Create the indicator.
        self.indicator = appindicator.Indicator.new(APPINDICATOR_ID, self.icon_bright, appindicator.IndicatorCategory.SYSTEM_SERVICES)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.menu)

        # Populate the menu with connected displays.
        self.ev_detect_displays()

    def ev_detect_displays(self, source=None):
        display_ids = get_connected_displays()

        # Remove old displays.
        for id in display_ids:
            if id in self.displays:
                display = self.displays[id]
                display.remove_from(self.menu)
                display.destroy()
                del self.displays[id]

        # Add new displays.
        for id in display_ids:
            display = Display(self, id)
            display.prepend_to(self.menu)
            self.displays[id] = display

        self.menu.show_all()

    def ev_toggle_autostart(self, source):
        if source.get_active():
            create_autostart()
        else:
            remove_autostart()
        source.set_active(check_autostart())

    def show(self):
        gtk.main()

    def ev_quit(self, source):
        """Stop everything. For when the user wants to quit."""
        gtk.main_quit()

    def update_icon(self, level):
        if self.indicator is not None:
            if level >= 0.99:
                self.indicator.set_icon(self.icon_bright)
            elif level > 0.3:
                self.indicator.set_icon(self.icon_dim)
            else:
                self.indicator.set_icon(self.icon_dark)


def main():
    BrightnessIndicator().show()

if __name__ == "__main__":
    main()
