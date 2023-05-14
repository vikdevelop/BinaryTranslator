#!/usr/bin/python3
import sys
import os
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib

class BTWindow(Gtk.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title("Binary translator")
        self.headerbar = Gtk.HeaderBar.new()
        self.set_titlebar(titlebar=self.headerbar)
        self.application = kwargs.get('application')
        
        self.set_size_request(120, 600)
        
        # App menu
        self.menu_button_model = Gio.Menu()
        self.menu_button_model.append("About app", 'app.about')
        self.menu_button = Gtk.MenuButton.new()
        self.menu_button.set_icon_name(icon_name='open-menu-symbolic')
        self.menu_button.set_menu_model(menu_model=self.menu_button_model)
        self.headerbar.pack_end(child=self.menu_button)
        
        # Translate button
        self.translateButton = Gtk.Button.new()
        self.tr_button_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 5)
        self.tr_button_box.append(Gtk.Image.new_from_icon_name( \
            'transmission-symbolic'))
        self.tr_button_box.append(Gtk.Label.new("Translate"))
        self.translateButton.set_child(self.tr_button_box)
        self.translateButton.set_can_focus(True)
        self.translateButton.add_css_class('suggested-action')
        self.translateButton.connect("clicked", self.translation)
        self.headerbar.pack_start(self.translateButton)
        
        # primary Gtk.Box
        self.binaryBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=30)
        self.binaryBox.set_halign(Gtk.Align.CENTER)
        self.binaryBox.set_valign(Gtk.Align.CENTER)
        self.set_child(self.binaryBox)
        
        # Title Image (Binary Translator icon)
        self.titleImage = Gtk.Image.new_from_icon_name("io.github.vikdevelop.BinaryTranslator")
        self.titleImage.set_pixel_size(64)
        self.binaryBox.append(self.titleImage)
        
        # Label about Binary Translator
        self.titleLabel = Gtk.Label.new()
        self.titleLabel.set_markup("<big><b>Binary translator</b></big>\nTranslate text to binary and vice versa.")
        self.titleLabel.set_justify(Gtk.Justification.CENTER)
        self.binaryBox.append(self.titleLabel)
        
        # List Box for entries 
        self.entryBox = Gtk.ListBox.new()
        self.entryBox.set_selection_mode(mode=Gtk.SelectionMode.NONE)
        self.entryBox.add_css_class(css_class='boxed-list')
        self.binaryBox.append(self.entryBox)
        
        # Input entry
        self.inputEntry = Adw.EntryRow.new()
        self.inputEntry.set_title("Enter normal or binary text to translate")
        self.entryBox.append(self.inputEntry)
        
        # Output entry
        self.outputEntry = Adw.EntryRow()
        self.outputEntry.set_title("Output of normal or binary text")
        self.outputEntry.set_editable(False)
        self.entryBox.append(self.outputEntry)
        
    # Translate text to binary and vice versa
    def translation(self, w):
        input_e = self.inputEntry.get_text()
        if "1" in input_e:
            def binary_to_string(input_e):
                # Split the binary string into groups of 8 bits
                binary_list = [input_e[i:i+8] for i in range(0, len(input_e), 8)]
                # Convert each group of 8 bits to its corresponding character
                result = ''.join([chr(int(binary, 2)) for binary in binary_list])
                return result

            string_output = binary_to_string(input_e)
            string_output.encode('utf-8')
            self.outputEntry.set_text(string_output)
        else:
            res = ''.join(format(ord(i), '08b') for i in input_e)
            self.outputEntry.set_text(res)
        
class BTApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.create_action('about', self.on_about_action, ["F1"])
        self.connect('activate', self.on_activate)
        
    def on_about_action(self, action, param):
        dialog = Adw.AboutWindow(transient_for=app.get_active_window())
        dialog.set_application_name("Binary translator")
        dialog.set_developer_name("vikdevelop")
        #dialog.set_translator_credits(_["translator_credits"])
        dialog.set_license_type(Gtk.License(Gtk.License.GPL_3_0))
        dialog.set_website("https://github.com/vikdevelop/BinaryTranslator")
        dialog.set_issue_url("https://github.com/vikdevelop/BinaryTranslator")
        dialog.set_copyright("© 2023 vikdevelop")
        dialog.set_developers(["vikdevelop https://github.com/vikdevelop"])
        version = "1.0"
        icon = "io.github.vikdevelop.BinaryTranslator"
        dialog.set_version(version)
        dialog.set_application_icon(icon)
        dialog.show()    
    
    def create_action(self, name, callback, shortcuts=None):
        action = Gio.SimpleAction.new(name, None)
        action.connect('activate', callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f'app.{name}', shortcuts)
    
    def on_activate(self, app):
        self.win = BTWindow(application=app)
        self.win.present()
app = BTApp()
app.run(sys.argv)
