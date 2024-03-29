#!/usr/bin/python3
import sys
import os
import locale
import json
import subprocess
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib
from pathlib import Path

# Detect system language
p_lang = locale.getlocale()[0]
r_lang = p_lang[:-3]

# Mechanism for checking application environment/runtime
flatpak = os.path.exists("/.flatpak-info")
snap = os.environ.get('SNAP_NAME', '') == 'binarytranslator'

# Check what environment the application is running in
if flatpak:
    try:
        locale = open(f"/app/translations/{r_lang}.json")
    except:
        locale = open("/app/translations/en.json")
    DATA = f"{Path.home()}/.var/app/io.github.vikdevelop.BinaryTranslator/data"
elif snap:
    try:
        locale = open(f"{os.getenv('SNAP')}/usr/translations/{r_lang}.json")
    except:
        locale = open("{os.getenv('SNAP')}/usr/translations/en.json")
    DATA = f"{os.getenv('SNAP_USER_DATA')}/.local/share"

# Load translation file
_ = json.load(locale)

# Application window
class BTWindow(Gtk.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title("Binary translator")
        self.headerbar = Gtk.HeaderBar.new()
        self.set_titlebar(titlebar=self.headerbar)
        self.application = kwargs.get('application')
        self.connect("close-request", self.on_close)
        
        # Connect to GSettings database
        self.settings = Gio.Settings.new_with_path("io.github.vikdevelop.BinaryTranslator", "/io/github/vikdevelop/BinaryTranslator/")
        
        self.set_size_request(503, 606)
        
        (width, height) = self.settings["window-size"]
        self.set_default_size(width, height)
        
        if self.settings["is-maximized"]:
            self.maximize()
        
        # Button for showing about dialog
        self.menu_button = Gtk.Button.new_from_icon_name("help-about-symbolic")
        self.menu_button.set_tooltip_text(_["about_app"])
        self.menu_button.connect("clicked", self.about)
        self.headerbar.pack_end(child=self.menu_button)
        
        # Button for showing dialog with saved binary texts
        self.textsButton = Gtk.Button.new_from_icon_name("list-drag-handle-symbolic")
        self.textsButton.add_css_class("flat")
        self.textsButton.set_tooltip_text(_["saved_binary_texts"])
        self.textsButton.connect("clicked", self.saved_dialog)
        self.headerbar.pack_end(child=self.textsButton)
        
        # Translate button
        self.translateButton = Gtk.Button.new()
        self.tr_button_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 5)
        self.tr_button_box.append(Gtk.Image.new_from_icon_name( \
            'transmission-symbolic'))
        self.tr_button_box.append(Gtk.Label.new(_["translate"]))
        self.translateButton.set_child(self.tr_button_box)
        self.translateButton.set_can_focus(True)
        self.translateButton.add_css_class('suggested-action')
        self.translateButton.connect("clicked", self.translation_button_clicked)
        self.headerbar.pack_start(self.translateButton)
        
        # primary Gtk.Box
        self.binaryBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=30)
        self.binaryBox.set_halign(Gtk.Align.CENTER)
        self.binaryBox.set_valign(Gtk.Align.CENTER)
        self.set_child(self.binaryBox)
        
        # Toast overlay
        self.toast_overlay = Adw.ToastOverlay.new()
        self.toast_overlay.set_margin_top(margin=1)
        self.toast_overlay.set_margin_end(margin=1)
        self.toast_overlay.set_margin_bottom(margin=1)
        self.toast_overlay.set_margin_start(margin=1)
        
        self.set_child(self.toast_overlay)
        self.toast_overlay.set_child(self.binaryBox)
        
        # Title Image (Binary Translator icon)
        self.titleImage = Gtk.Image.new_from_icon_name("io.github.vikdevelop.BinaryTranslator")
        self.titleImage.set_pixel_size(128)
        self.binaryBox.append(self.titleImage)
        
        # Label about Binary Translator
        self.titleLabel = Gtk.Label.new()
        self.titleLabel.set_markup(f"<big><b>Binary translator</b></big>\n{_['bt_desc']}")
        self.titleLabel.set_justify(Gtk.Justification.CENTER)
        self.binaryBox.append(self.titleLabel)
        
        # List Box for entries 
        self.entryBox = Gtk.ListBox.new()
        self.entryBox.set_selection_mode(mode=Gtk.SelectionMode.NONE)
        self.entryBox.add_css_class(css_class='boxed-list')
        self.binaryBox.append(self.entryBox)
        
        # Input entry
        self.inputEntry = Adw.EntryRow.new()
        self.inputEntry.set_title(_["input_entry"])
        self.entryBox.append(self.inputEntry)
        
        # Output entry
        self.outputEntry = Adw.EntryRow()
        self.outputEntry.set_title(_["output_entry"])
        self.outputEntry.set_editable(False)
        self.entryBox.append(self.outputEntry)
        
    def translation_button_clicked(self, w):
        self.translation()
    
    # Translate text to binary and vice versa
    def translation(self):
        input_e = self.inputEntry.get_text()
        if "1" in input_e:
            def binary_to_string(input_e):
                if " " in input_e:
                    o_e = f"{input_e}"
                    old_e = o_e.replace(" ", "")
                    input_e = f"{old_e}"
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
            without_spaces = input_e.replace(" ", "_")
            if not os.path.exists(f"{DATA}/binaries.txt"):
                with open(f"{DATA}/binaries.txt", "w") as b:
                    b.write(f'{without_spaces}')
            else:
                # Check if the string from the input entry exists in the DATA/binaries.txt file
                with open(f"{DATA}/binaries.txt") as rb:
                    f = rb.read()
                    if without_spaces in f:
                        print("It is exists.")
                    else:
                        with open(f"{DATA}/binaries.txt", "a") as wb:
                            wb.write(f'\n{without_spaces}')
    
    # Dialog for selecting saved binary texts
    def saved_dialog(self, w):
        self.TextDialog = Adw.MessageDialog.new(self)
        self.TextDialog.set_heading(_["saved_binary_texts"])
        self.TextDialog.set_body_use_markup(True)
        
        # Box for appending widgets
        self.setdBox = Gtk.ListBox.new()
        self.setdBox.set_selection_mode(mode=Gtk.SelectionMode.NONE)
        self.setdBox.get_style_context().add_class(class_name='boxed-list')
        self.TextDialog.set_extra_child(self.setdBox)
        
        self.TextDialog.add_response('cancel', _["cancel"])
        
        # Check, if data exists in the DATA/binaries.txt file
        if os.path.exists(f"{DATA}/binaries.txt"):
            self.binaries_in = subprocess.getoutput(f"cat {DATA}/binaries.txt")
            self.binaries_out = self.binaries_in.split()
            if self.binaries_out == []:
                self.TextDialog.set_body(_["saved_binary_texts_warning"])
            else:
                self.TextDialog.add_response('remove', _["remove"])
                self.show_text()
        else:
            self.TextDialog.set_body(_["saved_binary_texts_warning"])
            
        self.TextDialog.set_response_appearance('remove', Adw.ResponseAppearance.DESTRUCTIVE)
        self.TextDialog.connect('response', self.dialog_response)
        
        self.TextDialog.show()
    
    # Display data in the dialog window from the DATA/binaries.txt file
    def show_text(self):
        actions = Gtk.StringList.new(strings=self.binaries_out)
        
        self.import_row = Adw.ComboRow.new()
        self.import_row.set_use_markup(True)
        self.import_row.set_use_underline(True)
        self.import_row.set_title("")
        self.import_row.set_title_lines(2)
        self.import_row.set_subtitle_lines(4)
        self.import_row.set_model(model=actions)
        self.setdBox.append(child=self.import_row)
        self.TextDialog.add_response('ok', _["use"])
        self.TextDialog.set_response_appearance('ok', Adw.ResponseAppearance.SUGGESTED)
    
    # Response after clicking on any button in the dialog
    def dialog_response(self, w, response):
        sel_item = self.import_row.get_selected_item()
        item_with_dashes = sel_item.get_string()
        item_with_spaces = item_with_dashes.replace("_", " ")
        # Response after clicking on "Use" button
        if response == 'ok':
            self.settings["use-string"] = True
            self.inputEntry.set_text(item_with_spaces)
            self.translation()
        # Response after clicking on "Remove" button
        elif response == 'remove':
            os.system(f"sed -i 's\%s\ \ ' %s/binaries.txt" % (sel_item.get_string(), DATA))
            # Show toast message about removed string
            self.toast = Adw.Toast.new(title=f'{item_with_spaces} {_["removed"]}')
            self.toast_overlay.add_toast(self.toast)
            
    # Show about dialog
    def about(self, w):
        dialog = Adw.AboutWindow(transient_for=app.get_active_window())
        dialog.set_application_name("Binary translator")
        dialog.set_developer_name("vikdevelop")
        if r_lang == 'en':
            print("")
        else:
            dialog.set_translator_credits(_["translator_credits"])
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
    
    # Action after closing the application window
    def on_close(self, widget, *args):
        (width, height) = self.get_default_size()
        self.settings["window-size"] = (width, height)
        self.settings["is-maximized"] = self.is_maximized()
        self.settings["use-string"] = False
        self.settings["removing-strings"] = False
        self.settings["string"] = ""
        
class BTApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.connect('activate', self.on_activate)
    
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
