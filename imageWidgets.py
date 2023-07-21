import customtkinter as ctk
from tkinter import filedialog, Canvas
from settings import *

class ImageImport(ctk.CTkFrame):
    def __init__(self, parent, import_funciton):
        super().__init__(master = parent)
        self.grid(column = 0, columnspan = 2, row = 0, sticky = 'nsew')
        self.import_funciton = import_funciton
        ctk.CTkButton(self, text = 'open image', command = self.open_dialog).pack(expand = True)

    def open_dialog(self):
        path = filedialog.askopenfile().name
        self.import_funciton(path)

class ImageOutput(Canvas):
    def __init__(self, parent, resize_image):
        super().__init__(master = parent, background = BACKGROUND_COLOR, bd = 0, highlightthickness = 0, relief = 'ridge')
        self.pack(fill = 'both', expand = True)
        self.bind('<Configure>', resize_image)

class CloseOutput(ctk.CTkButton):
    def __init__(self,parent, close_func):
        super().__init__(master = parent,
            command = close_func, 
            text = 'x', 
            text_color = WHITE, 
            fg_color = 'transparent', 
            width = 40, 
            height = 40, 
            corner_radius = 0, 
            hover_color = CLOSE_RED)
        self.place(relx = 0.99, rely = 0.01, anchor = 'ne')