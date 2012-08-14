# Copyright (C) 2012  Mathias Brodala <info@noctus.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gtk

from xl.nls import gettext as _
from xl import event
from xlgui import main

MAINMENUBUTTON = None

def enable(exaile):
    """
        Enables the plugin
    """
    try:
        gtk.Notebook.get_action_widget
    except AttributeError:
        raise NotImplementedError(_('This plugin needs at least '
                                    'PyGTK 2.22 and GTK 2.20.'))
    else:
        if exaile.loading:
            event.add_callback(on_gui_loaded, 'gui_loaded')
        else:
            on_gui_loaded()

def disable(exaile):
    """
        Disables the plugin
    """
    if MAINMENUBUTTON:
        MAINMENUBUTTON.destroy()

def on_gui_loaded(*args):
    """
        Creates the main menu button
        which takes care of the rest
    """
    global MAINMENUBUTTON

    MAINMENUBUTTON = MainMenuButton()

class MainMenuButton(gtk.ToggleButton):
    """
    """
    __gsignals__ = {}

    def __init__(self):
        """
            Adds the button to the main window 
            and moves the main menu items
        """
        gtk.Button.__init__(self)

        self.set_image(gtk.image_new_from_icon_name('exaile', gtk.ICON_SIZE_BUTTON))
        self.set_tooltip_text(_('Main Menu'))
        self.set_focus_on_click(True)
        self.set_relief(gtk.RELIEF_NONE)

        builder = main.mainwindow().builder

        # Insert button at the top of the panel notebook
        self.panel_notebook = builder.get_object('panel_notebook')
        self.panel_notebook.set_action_widget(self, gtk.PACK_START)

        # Move menu items of the main menu to the internal menu
        self.mainmenu = builder.get_object('mainmenu')
        self.menu = gtk.Menu()
        self.menu.attach_to_widget(self, self.on_menu_detach)
        self.menu.connect('map', self.on_menu_map)
        self.menu.connect('deactivate', self.on_menu_deactivate)

        for menuitem in self.mainmenu:
            menuitem.reparent(self.menu)

        self.menu.show_all()
        self.show_all()

    def destroy(self):
        """
            Moves the main menu items back and
            removes the button from the main window
        """
        for menuitem in self.menu:
            menuitem.reparent(self.mainmenu)

        self.unparent()
        gtk.Button.destroy(self)

    def get_menu_position(self, menu):
        """
            Positions the menu at the right of the button
        """
        # Origin includes window position and decorations
        x, y = self.props.window.get_origin()
        allocation = self.get_allocation()

        return (
            x + allocation.x + allocation.width,
            y + allocation.y,
            False
        )

    def do_button_press_event(self, e):
        """
            Pops out the menu upon click
        """
        if e.button == 1:
            self.menu.popup(None, None,
                self.get_menu_position, e.button, e.time)

        return True

    def do_popup_menu(self):
        """
            Pops out the menu upon pressing 
            the Menu or Shift+F10 keys
        """
        self.menu.popup(None, None,
            self.get_menu_position, 0, gtk.get_current_event_time())
        
        return True

    def on_menu_detach(self, menu, widget):
        """
            Dummy method to be used with
            gtk.Menu.attach_to_widget()
        """
        pass

    def on_menu_map(self, widget):
        """
            Indicates button activation upon menu popup
        """
        self.set_active(True)

    def on_menu_deactivate(self, menu):
        """
            Removes button activation upno menu popdown
        """
        self.set_active(False)
