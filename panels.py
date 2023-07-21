import customtkinter as ctk
from tkinter import filedialog
from settings import *

class Panel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master = parent, fg_color = DARK_GRAY)
        self.pack(fill = 'x', pady = 4, ipady = 8)

class SliderPanel(Panel):
    def __init__(self, parent, text, data_val, min_val, max_val):
        super().__init__(parent = parent)
        #layout
        self.rowconfigure((0,1), weight = 1)
        self.columnconfigure((0,1), weight = 1)
        self.data_val = data_val
        self.data_val.trace('w', self.update_text)
        ctk.CTkLabel(self, text = text).grid(column = 0, row = 0, sticky = 'W', padx = 8)
        self.num_label = ctk.CTkLabel(self, text = data_val.get())
        self.num_label.grid(column = 1, row = 0, sticky = 'E', padx = 8)
        ctk.CTkSlider(self,
            fg_color = SLIDER_BG,
            variable = self.data_val,
            from_ = min_val, 
            to = max_val).grid(row = 1, column = 0, columnspan = 2, sticky = 'ew', padx = 8, pady = 4)

    def update_text(self, *args):
        self.num_label.configure(text = f"{round(self.data_val.get(), 2)}")

class SegmentPanel(Panel):
    def __init__(self, parent, text, data_var, options):
        super().__init__(parent = parent)
        ctk.CTkLabel(self, text = text).pack()
        ctk.CTkSegmentedButton(self, values = options, variable = data_var).pack(expand = True, fill = 'both', padx = 4, pady = 4)

class SwitchPanel(Panel):
    def __init__(self, parent, *args):
        super().__init__(parent = parent)
        for var, text, in args:
            switch = ctk.CTkSwitch(self, text = text, variable = var, button_color = BLUE, fg_color = SLIDER_BG)
            switch.pack(side = 'left', expand = True, fill = 'both', padx = 5, pady = 5)

class IntEntryPanel(Panel):
    def __init__(self, parent, text, entry_var, min_val=-999999999999, max_val=999999999999):
        super().__init__(parent = parent)
        self.data_val = entry_var
        self.data_val.trace("w", self.revert_label)
        self.max = max_val
        self.min = min_val
        ctk.CTkLabel(self, text = text).pack()
        self.num_label = ctk.CTkLabel(self, text = self.data_val.get())
        self.num_label.pack()
        self.entry = ctk.CTkEntry(self)
        self.entry.pack(fill = 'x', padx = 20, pady = 5)
        self.button = ctk.CTkButton(self, text = "Enter", command = self.enter)
        self.button.pack()

    def revert_label(self, *args):
        if (self.data_val.get() == 0):
            self.num_label.configure(text = self.data_val.get())
            self.entry.delete(0, ctk.END)
            
    def enter(self):
        try:
            hold = int(self.entry.get())
            if (hold > self.max or hold < self.min):
                self.num_label.configure(text = f"You did not enter a number between {self.min} and {self.max}.")
            else:
                self.num_label.configure(text = f"{hold}")
                self.data_val.set(hold)
        except ValueError:
            self.num_label.configure(text = "You did not enter an integer")


class FileNamePanel(Panel):
    def __init__(self, parent, name_string, file_string):
        super().__init__(parent = parent)
        self.file_string = file_string
        self.name_string = name_string
        self.name_string.trace('w', self.update_text)
        ctk.CTkLabel(self, text = "File Name").pack()
        ctk.CTkEntry(self, textvariable = self.name_string).pack(fill = 'x', padx = 20, pady = 5)
        frame = ctk.CTkFrame(self, fg_color = 'transparent')
        jpg_check = ctk.CTkCheckBox(frame, text = 'jpg', variable = self.file_string, command = lambda: self.click('jpg'), onvalue = 'jpg' , offvalue = 'png').pack(side = 'left', fill = 'x', expand = True)
        png_check = ctk.CTkCheckBox(frame, text = 'png', variable = self.file_string, command = lambda: self.click('png'), onvalue = 'png', offvalue = 'jpg').pack(side = 'left', fill = 'x', expand = True)
        frame.pack(expand = True, fill = 'x', padx = 20)
        self.output = ctk.CTkLabel(self, text = '')
        self.output.pack()

    def click(self, value):
        self.file_string.set(value)
        self.update_text()

    def update_text(self, *args):
        if self.name_string.get():
            text = self.name_string.get().replace(" ", "_") + "." + self.file_string.get()
            self.output.configure(text = text)

class FilePathPanel(Panel):
    def __init__(self, parent, path_string):
        super().__init__(parent = parent)
        self.path_string = path_string
        ctk.CTkLabel(self, text = "Path").pack()
        export = ctk.CTkButton(self, text = "Open Explorer", command = self.open_file_dialog).pack(pady = 5)
        entry = ctk.CTkEntry(self, textvariable = self.path_string).pack(expand = True, fill = 'both', padx = 5, pady = 5)

    def open_file_dialog(self):
        self.path_string.set(filedialog.askdirectory())

class DropDownPanel(ctk.CTkOptionMenu):
    def __init__(self, parent, data_var, options):
        super().__init__(master = parent, values = options, fg_color = DARK_GRAY, button_color = DROPDOWN_MAIN_COLOR, button_hover_color = DROWPDOWN_HOVER_COLOR, dropdown_fg_color = DROWPDOWN_MENU_COLOR, variable = data_var)
        self.pack(fill = 'x', pady = 4)

class RevertButton(ctk.CTkButton):
    def __init__(self, parent, *args):
        super().__init__(master = parent, text = "Revert", command = self.revert)
        self.pack(side = 'bottom', pady = 10)
        self.args = args

    def revert(self):
        for var, default in self.args:
            var.set(default)

class SaveButton(ctk.CTkButton):
    def __init__(self, parent, export_image, name, file_str, path):
        super().__init__(master = parent, text = "Export", command = self.export)
        self.pack(side = 'bottom', pady = 10)
        self.export_image = export_image
        self.name = name
        self.file_str = file_str
        self.path = path

    def export(self):
        self.export_image(self.name.get(), self.file_str.get(), self.path.get())
