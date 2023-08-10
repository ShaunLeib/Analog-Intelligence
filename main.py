import customtkinter as ctk
import tkinter as tk
from imageWidgets import *
import cv2
from menu import Menu
from imageWindow import ImageWindow
from selection import Rectangle, Circle, Polygon, Free

# TODO:
# Get tools to just modify selected area (IDEA: invert mask & and merge)
# Add error handling if free hand or poly selection isn't enclosed
# organize code better
# Unselect option
# in merge in image_window.py see comment


class App(ctk.CTk):
    def __init__(self):
        # setup
        super().__init__()
        ctk.set_appearance_mode('dark')
        self.geometry('500x1300+40+100')
        self.title('Tools')
        self.minsize(100, 1300)
        self.image_params = self.init_params()
        self.tools_params = self.init_tools()
        self.images_arr = []
        self.params_arr = []
        self.params_arr.append(self.image_params)
        self.current_tab = ctk.IntVar(value = 0)
        self.current_tab.trace('w', self.tab_changed)
        self.current_params = self.params_arr[self.current_tab.get()]

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
    
    def init_tools(self):
        tools_params = {
            "new" : ctk.IntVar(value = 0),
            "red" : ctk.IntVar(value = 0),
            "green" : ctk.IntVar(value = 0),
            "blue" : ctk.IntVar(value = 0),
            "select" : ctk.IntVar(value = 0)
        }
        self.trace_tools_vars(tools_params)
        return tools_params

    def trace_tools_vars(self, tools_params):
        tools_params['new'].trace('w', self.new_image_window)
        tools_params['red'].trace('w', self.new_image_window)
        tools_params['green'].trace('w', self.new_image_window)
        tools_params['blue'].trace('w', self.new_image_window)
        tools_params['select'].trace('w', self.image_select)

    def trace_image_vars(self, image_params):
        for dict in image_params.values():
            for var in dict.values():
                var.trace("w", self.update_params)

    def update_params(self, *args):
        self.images_arr[self.current_tab.get()].manipulate_image(self.params_arr[self.current_tab.get()])
    
    def change_current_tab(self, event):
        self.current_tab.set(self.image_window.get_currently_selected_tab())

    def tab_changed(self, *args):
        if len(self.images_arr) != 0:
            self.current_image = self.images_arr[self.current_tab.get()]
            self.current_params = self.params_arr[self.current_tab.get()]
            self.menu.update_params(self.current_params['position'], self.current_params['convolution'], self.current_params['color'], self.current_params['effect'], self.tools_params, self.export_image)

    def new_image_window(self, *args):
        if self.tools_params['new'].get() == 1:
            path = tk.filedialog.askopenfile()
            if path is not None:
                path = path.name
                new_params = self.init_params()
                self.params_arr.append(new_params)
                self.images_arr.append(self.image_window.add_secondary_image(cv2.imread(path), new_params))
                self.tools_params['new'].set(0)
            else:
                tk.messagebox.showinfo(title = "Error", message = "No path entered.")

    def image_select(self, *args):
        selection = self.tools_params["select"].get()
        if selection == 1:
            done = ctk.IntVar(value = 0)
            self.image_window.resizable(False, False)
            free = Free(self.image_window, done)
            free.select()
            self.wait_variable(done)
            self.image_window.resizable(True, True)
        elif selection == 2:
            done = ctk.IntVar(value = 0)
            self.image_window.resizable(False, False)
            rect = Rectangle(self.image_window, done)
            rect.select()
            self.wait_variable(done)
            self.image_window.resizable(True, True)
        elif selection == 3:
            done = ctk.IntVar(value = 0)
            self.image_window.resizable(False, False)
            circ = Circle(self.image_window, done)
            circ.select()
            self.wait_variable(done)
            self.image_window.resizable(True, True)
        elif selection == 4:
            done = ctk.IntVar(value = 0)
            self.image_window.resizable(False, False)
            poly = Polygon(self.image_window, done)
            poly.select()
            self.wait_variable(done)
            self.image_window.resizable(True, True)

    def import_image(self, path):
        self.current_tab.set(0)
        self.image_import.grid_forget()
        self.image_window = ImageWindow(self, self.change_current_tab)
        self.images_arr.append(self.image_window.add_main_image(cv2.imread(path), self.image_params))
        self.current_image = self.images_arr[self.current_tab.get()]
        self.image_window.exists.trace('w', self.image_window_closed)
        self.menu = Menu(self, self.current_params['position'], self.current_params['convolution'], self.current_params['color'], self.current_params['effect'], self.tools_params, self.export_image)


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
            image = self.images_arr[0].get_image()
            cv2.imwrite(export_path, image)
            self.image_window.close_edit()

root = App()
root.mainloop()