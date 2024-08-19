"""
This is a basic password manager that saves passwords in a png image.
"""

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW #type: ignore
import toga.widgets # type: ignore


def temp_action(widget:toga.Widget):
    print(f"Menu item {widget.text} triggered action") #type: ignore


class ImageManager(toga.App):
    def startup(self):
        """Construct and show the Toga application.

        Usually, you would add your application to a main content box.1`
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        main_box = toga.Box(style=Pack(direction=COLUMN))

        self.main_window:toga.MainWindow = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.menubar = toga.ScrollContainer(id="menubar", vertical=False)
        self.main_window.content.add(self.menubar) #type: ignore

        #Add file option commands
        self.file_commands: list[toga.Button] = []
        self.file_commands.append(toga.Button(on_press=temp_action, text="Save"))
        self.file_commands.append(toga.Button(on_press=temp_action, text="Export"))
        self.file_commands.append(toga.Button(on_press=temp_action, text="Import"))
        self.file_commands.append(toga.Button(on_press=temp_action, text="Clear"))
        self.file_commands.append(toga.Button(on_press=temp_action, text="Open..."))
        self.file_commands.append(toga.Button(on_press=temp_action, text="Convert File"))

        #Add setting option commands
        self.setting_commands: list[toga.Button] = []
        self.setting_commands.append(toga.Button(on_press=temp_action, text="Change Bits"))
        self.setting_commands.append(toga.Button(on_press=temp_action, text="Startup Image"))
        self.setting_commands.append(toga.Button(on_press=temp_action, text="Image Path"))
        self.setting_commands.append(toga.Button(on_press=temp_action, text="Delete Image Path"))
        self.setting_commands.append(toga.Button(on_press=temp_action, text="Ask for Key"))
        self.setting_commands.append(toga.Button(on_press=temp_action, text="Edit New Passwords"))
        self.setting_commands.append(toga.Button(on_press=temp_action, text="Reset to Default"))

        Image_options = toga.Command(self.show_options, text="Image Options", order=0)# type: ignore
        settings = toga.Command(self.show_settings, text="Settings", order=0)# type: ignore

        self.main_window.toolbar.add(Image_options, settings)


        self.main_window.show()


    def show_settings(self, widget):
        self.hide_options()
        if self.hide_settings():
            return
        
        self.settings = toga.Box("settings")
        for command in self.setting_commands:
            self.settings.add(command)

        
        self.menubar.content = self.settings
        #self.main_window.content.add(self.settings) # type: ignore
    
    def hide_settings(self):
        if not "settings" in self.app.widgets._registry:
            return False
        
        self.menubar.content.remove(self.settings) # type: ignore
        self.menubar.content = None
        return True
    
    def show_options(self, widget):
        self.hide_settings()
        if self.hide_options():
            return
        
        self.options = toga.Box("options")
        for command in self.file_commands:
            self.options.add(command)

        self.menubar.content = self.options
        #self.main_window.content.add(self.options) # type: ignore
    
    def hide_options(self):
        if not "options" in self.app.widgets._registry:
            return False
        
        self.menubar.content.remove(self.options) # type: ignore
        self.menubar.content = None
        return True


def main():
    return ImageManager()
