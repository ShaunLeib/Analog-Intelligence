import customtkinter as ctk
import tkinter as tk
from imageWidgets import *
import cv2
from PIL import Image, ImageTk, ImageOps, ImageEnhance, ImageFilter
from menu import Menu
from imageWindow import ImageWindow
from secondaryImageWindow import SecondaryImageWindow
import numpy as np
        

class App(ctk.CTk):
    def __init__(self):
        
        # setup
        super().__init__()
        ctk.set_appearance_mode('dark')
        self.geometry('500x1300+40+100')
        self.title('Tools')
        self.minsize(100, 1300)
        self.image_params = self.init_params()
        self.secondary_windows = self.init_secondary()

        # layout
        self.rowconfigure(0, weight = 1)
        self.columnconfigure(0, weight = 2, uniform = 'a')
        self.columnconfigure(1, weight = 6, uniform = 'a')


        self.image_import = ImageImport(self, self.import_image)
        

    def init_params(self):
        image_params = {
            "position" : {
                'rotate' : ctk.DoubleVar(value = ROTATE_DEFAULT),
                'flip' : ctk.StringVar(value = FLIP_OPTIONS[0])
            },
            "convolution" : {
                'four_edge' : ctk.BooleanVar(value = FOUR_WAY_EDGE_DEFAULT),
                'blur' : ctk.BooleanVar(value = BLUR_2_DEFAULT),
                'sharpen' : ctk.BooleanVar(value = SHARPEN_DEFAULT),
                'point' : ctk.BooleanVar(value = POINT_EDGE_DEFAULT),
                'shadow_floor' : ctk.IntVar(value = SHADOW_FLOOR_DEFAULT),
                'highlight_ceiling' : ctk.IntVar(value = HIGHLIGHT_CEILING_DEFAULT)
            },
            "color" : {
                'brightness' : ctk.DoubleVar(value = BRIGHTNESS_DEFAULT),
                'grayscale' : ctk.BooleanVar(value = GRAYSCALE_DEFAULT),
                'invert' : ctk.BooleanVar(value = INVERT_DEFAULT),
                'vibrance' : ctk.DoubleVar(value = VIBRANCE_DEFAULT)
            },
            "effect" : {
                'blur' : ctk.DoubleVar(value = BLUR_DEFAULT),
                'contrast' : ctk.IntVar(value = CONTRAST_DEFUALT)
            }
        }
        self.trace_image_vars(image_params)
        return image_params
    
    def init_secondary(self):
        secondary_windows = {
            "new" : ctk.IntVar(value = 0),
            "red" : ctk.IntVar(value = 0),
            "green" : ctk.IntVar(value = 0),
            "blue" : ctk.IntVar(value = 0)
        }
        self.trace_secondary_vars(secondary_windows)
        return secondary_windows 
        #1. add var here
        #2. Add to var to Menu in import_image
        #3. in menu change: init, coresponding frame, frame class param, add panel to class
        #4. trace it
        #5. make image manipulation logic

        #get changes from slider

        #tracing
        

    def trace_secondary_vars(self, secondary_windows):
        secondary_windows['new'].trace('w', self.new_image_window)

    def trace_image_vars(self, image_params):
        for dict in image_params.values():
            for var in dict.values():
                var.trace("w", self.update_params)

    def update_params(self, *args):
        self.image_window.manipulate_image(self.image_params)
    
    def new_image_window(self, *args):
        if self.secondary_windows['new'].get() == 1:
            path = tk.filedialog.askopenfile().name
            self.secondary_original = cv2.imread(path)
            self.secondary_iamge_params = self.init_params()
            self.secondary_image_window = SecondaryImageWindow(self, self.secondary_iamge_params,self.secondary_original)
            # self.secondary_image_window.exist.trace("w", asdf)
            # SecondaryImageWindow()


    def import_image(self, path):
        self.original = cv2.imread(path)
        self.image_import.grid_forget()
        self.image_window = ImageWindow(self, self.image_params, self.original)
        self.image_window.exists.trace('w', self.image_window_closed)
        self.menu = Menu(self, self.image_params['position'], self.image_params['convolution'], self.image_params['color'], self.image_params['effect'], self.secondary_windows, self.export_image)


    def image_window_closed(self, *args):
        if self.image_window.exists.get() == 0:
            self.menu.pack_forget()
            self.image_import = ImageImport(self, self.import_image)
            self.image_window.destroy()
            self.image_params = self.init_params()
    
    def export_image(self, name, file_str, path):
        if path == "":
            tk.messagebox.showinfo(title = "Error", message = "You did not enter a path")
        elif name == "":
            tk.messagebox.showinfo(title = "Error", message = "You did not enter a name")
        else:
            export_path = f"{path}/{name}.{file_str}"
            image = self.image_window.get_image()
            cv2.imwrite(export_path, image)
            self.image_window.close_edit()

root = App()
root.mainloop()