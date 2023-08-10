import customtkinter as ctk
from panels import *


class Menu(ctk.CTkTabview):
    def __init__(self, parent, position, convolution, color, effect, tool_params, export_image):
        super().__init__(master=parent)
        self.pack(fill='both', expand=True)

        # tabs
        self.add("Home")
        self.add('Position')
        self.add("Convolutions")
        # self.add("Deep")
        self.add('Color')
        self.add('Effects')
        self.add("Select")
        self.add('Export')

        HomeFrame(self.tab("Home"), tool_params)
        PositionFrame(self.tab('Position'), position)
        ConvolutionFrame(self.tab("Convolutions"), convolution)
        ColorFrame(self.tab('Color'), color)
        EffectFrame(self.tab('Effects'), effect)
        SelectFrame(self.tab("Select"), tool_params)
        ExportFrame(self.tab('Export'), export_image)

    def update_params(self, position, convolution, color, effect, tool_params, export_image):
        self.delete("Home")
        self.delete('Position')
        self.delete("Convolutions")
        # self.delete("Deep")
        self.delete('Color')
        self.delete('Effects')
        self.delete("Select")
        self.delete('Export')
        self.add("Home")
        self.add('Position')
        self.add("Convolutions")
        # self.add("Deep")
        self.add('Color')
        self.add('Effects')
        self.add("Select")
        self.add('Export')

        HomeFrame(self.tab("Home"), tool_params)
        PositionFrame(self.tab('Position'), position)
        ConvolutionFrame(self.tab("Convolutions"), convolution)
        ColorFrame(self.tab('Color'), color)
        EffectFrame(self.tab('Effects'), effect)
        SelectFrame(self.tab("Select"), tool_params)
        ExportFrame(self.tab('Export'), export_image)


class HomeFrame(ctk.CTkFrame):
    def __init__(self, parent, tool_params):
        super().__init__(master=parent, fg_color='transparent')
        self.pack(expand=True, fill='both')
        self.tool_params = tool_params
        self.button = ctk.CTkButton(self, text="Open", command=self.open_new)
        self.button.pack()

    def open_new(self):
        self.tool_params['new'].set(1)


class SelectFrame(ctk.CTkFrame):
    def __init__(self, parent, select_params):
        super().__init__(master=parent, fg_color='transparent')
        self.pack(expand=True, fill='both')
        self.select_params = select_params
        ctk.CTkButton(self, text="Free", command=lambda: self.open_new(1)).pack()
        ctk.CTkButton(self, text="Rectangle", command=lambda: self.open_new(2)).pack()
        ctk.CTkButton(self, text="Circle", command=lambda: self.open_new(3)).pack()
        ctk.CTkButton(self, text="Polygon", command=lambda: self.open_new(4)).pack()

    def open_new(self, selection):
        self.select_params["select"].set(selection)


class PositionFrame(ctk.CTkFrame):
    def __init__(self, parent, position):
        super().__init__(master=parent, fg_color='transparent')
        self.pack(expand=True, fill='both')

        SliderPanel(self, "Rotation", position['rotate'], 0, 360)
        SegmentPanel(self, "Invert", position['flip'], FLIP_OPTIONS)
        RevertButton(self,
                     (position['rotate'], ROTATE_DEFAULT),
                     (position['flip'], FLIP_OPTIONS[0]))


class ColorFrame(ctk.CTkFrame):
    def __init__(self, parent, color):
        super().__init__(master=parent, fg_color='transparent')
        self.pack(expand=True, fill='both')

        SwitchPanel(self, (color['grayscale'], 'B/W'), (color['invert'], "Invert"))
        SliderPanel(self, "Brightness", color['brightness'], 0, 5)
        SliderPanel(self, "Vibrance", color['vibrance'], 0, 5)
        RevertButton(self,
                     (color['brightness'], BRIGHTNESS_DEFAULT),
                     (color['grayscale'], GRAYSCALE_DEFAULT),
                     (color['invert'], INVERT_DEFAULT),
                     (color['vibrance'], VIBRANCE_DEFAULT))


class EffectFrame(ctk.CTkFrame):
    def __init__(self, parent, effect):
        super().__init__(master=parent, fg_color='transparent')
        self.pack(expand=True, fill='both')

        SliderPanel(self, "Blur", effect['blur'], 0, 30)
        SliderPanel(self, "Contrast", effect['contrast'], 0, 10)
        RevertButton(self,
                     (effect['blur'], BLUR_DEFAULT),
                     (effect['contrast'], CONTRAST_DEFUALT))


class ConvolutionFrame(ctk.CTkFrame):
    def __init__(self, parent, convolution):
        super().__init__(master=parent, fg_color='transparent')
        self.pack(expand=True, fill='both')

        SwitchPanel(self, (convolution['four_edge'], "Four Way Edge Detection"), (convolution['blur'], "Blur"))
        SwitchPanel(self, (convolution['sharpen'], "Sharpen"), (convolution['point'], "Point Edges"))
        IntEntryPanel(self, "Shadow Floor", convolution['shadow_floor'], min_val=0, max_val=255)
        IntEntryPanel(self, "Highlight Ceiling", convolution['highlight_ceiling'], min_val=0, max_val=255)
        RevertButton(self,
                     (convolution['blur'], BLUR_2_DEFAULT),
                     (convolution['four_edge'], FOUR_WAY_EDGE_DEFAULT),
                     (convolution['sharpen'], SHARPEN_DEFAULT),
                     (convolution['point'], POINT_EDGE_DEFAULT),
                     (convolution["shadow_floor"], SHADOW_FLOOR_DEFAULT),
                     (convolution["highlight_ceiling"], HIGHLIGHT_CEILING_DEFAULT))


class ExportFrame(ctk.CTkFrame):
    def __init__(self, parent, export_image):
        super().__init__(master=parent, fg_color='transparent')
        self.pack(expand=True, fill='both')

        self.name_string = ctk.StringVar()
        self.file_string = ctk.StringVar(value='jpg')
        self.path_string = ctk.StringVar()

        FileNamePanel(self, self.name_string, self.file_string)
        FilePathPanel(self, self.path_string)
        SaveButton(self, export_image, self.name_string, self.file_string, self.path_string)
