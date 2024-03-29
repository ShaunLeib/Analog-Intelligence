import customtkinter as ctk
import tkinter as tk
import cv2
import settings
from PIL import Image, ImageTk, ImageOps, ImageEnhance, ImageFilter
from imageWidgets import *
import numpy as np


class ImageWindow(ctk.CTkToplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("Analog Intelligence")
        self.geometry("1700x1300+600+100")
        self.protocol('WM_DELETE_WINDOW', self.close_edit)
        self.minsize(800, 500)
        self.notebook = tk.ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)
        self.exists = ctk.IntVar(value=1)
        self.notebook.bind('<<NotebookTabChanged>>', callback)
        self.merge_button = ctk.CTkButton(self, text="Merge", command=self.merge)
        self.frame_array = []
        self.selection = False

    def add_main_image(self, image, params):
        new_image = ImageDisplay(self, image, params)
        self.frame_array.append(new_image)
        self.notebook.add(new_image, text="Main Image")
        return new_image

    def add_secondary_image(self, image, params):
        new_image = SecondaryImageDisplay(self, image, params)
        new_button = ctk.CTkButton(new_image, text="Merge", command=self.merge)
        new_button.pack(pady=10)
        self.frame_array.append(new_image)
        self.notebook.add(new_image, text="Secondary Image")
        new_image.exists.trace('w', self.delete_frame)
        return new_image

    def close_edit(self):
        if tk.messagebox.askokcancel("Close", "Do you want to continue?"):
            self.exists.set(0)
            self.notebook.pack_forget()

    def get_currently_selected_tab(self):
        return self.notebook.index(self.notebook.select())

    def delete_frame(self, *args):
        idx = self.get_currently_selected_tab()
        self.notebook.forget(idx)

    def merge(self): 
        indx = self.get_currently_selected_tab()
        if indx == 0:
            tk.messagebox.showinfo(title="Error", message="Unable to merge with main")
        else:
            main_image = self.frame_array[0]
            selected_image = self.frame_array[indx]
            if main_image.get_image_shape() != selected_image.get_image_shape():
                tk.messagebox.showinfo(title="Error", message=f"Image shapes don't match {main_image.get_image_shape()} vs {selected_image.get_image_shape()}")
            else:

                alpha = tk.simpledialog.askfloat(title="Alpha",
                                                prompt="Enter the percentage of blending you want with the main image. The higher the number, the more this image will show. Defualt = 0.5")
                if alpha is not None and alpha < 1 and alpha > 0:
                    beta = 1 - alpha
                    new_image = cv2.addWeighted(main_image.get_image(), beta, selected_image.get_image(), alpha, 0)
                    main_image.set_image(new_image)
                    self.notebook.forget(indx)
                else:
                    tk.messagebox.showinfo(title="Error", message="Number must be between 0-1.")

    def get_current_canvas(self):
        indx = self.get_currently_selected_tab()
        return self.frame_array[indx].get_canvas()

    def get_current_original_image_size(self):
        indx = self.get_currently_selected_tab()
        return self.frame_array[indx].get_original_image_size()

    def get_current_image_size(self):
        indx = self.get_currently_selected_tab()
        return self.frame_array[indx].get_image_size()

    def get_current_canvas_difference(self):
        indx = self.get_currently_selected_tab()
        return self.frame_array[indx].get_differences()

    def get_current_ratios(self):
        indx = self.get_currently_selected_tab()
        return self.frame_array[indx].get_ratios()

    def get_main_image(self):
        return self.frame_array[0].get_image()  # change export image with this

    def get_current_image(self):
        indx = self.get_currently_selected_tab()
        return self.frame_array[indx].get_image()

    def get_image_display(self):
        indx = self.get_currently_selected_tab()
        return self.frame_array[indx]




class ImageDisplay(ctk.CTkFrame):
    def __init__(self, parent, image, params):
        super().__init__(master=parent)
        self.image_output = ImageOutput(self, self.resize_image)

        self.original = image
        self.original_height, self.original_width = self.original.shape[:2]
        self.image = self.original
        self.image_params = params
        self.mask = None

        # canvas data
        self.image_width = 0
        self.image_height = 0
        self.canvas_width = 0
        self.canvas_height = 0

        self.image_height, self.image_width = self.image.shape[:2]
        self.image_ratio = self.image_width / self.image_height

    def set_image(self, image):
        self.original = image
        self.image = self.original
        self.place_image()

    def get_image(self):
        return self.image
    
    def get_image_shape(self):
        return self.image.shape

    def get_canvas(self):
        return self.image_output

    def get_original_image_size(self):
        return (self.original_height, self.original_width)

    def get_image_size(self):
        return (self.image_height, self.image_width)

    def get_differences(self):
        return self.vertical_canvas_difference, self.horizontal_canvas_difference

    def get_ratios(self):
        return self.vertical_ratio, self.horizonal_ratio

    def resize_image(self, event):
        self.canvas_ratio = event.width / event.height

        self.canvas_width = event.width
        self.canvas_height = event.height

        if self.canvas_ratio > self.image_ratio:
            self.image_height = event.height
            self.image_width = self.image_height * self.image_ratio
        else:
            self.image_width = event.width
            self.image_height = self.image_width / self.image_ratio
        self.horizontal_canvas_difference = (self.canvas_width - self.image_width) / 2
        self.vertical_canvas_difference = (self.canvas_height - self.image_height) / 2
        self.vertical_ratio = self.original_height / self.image_height
        self.horizonal_ratio = self.original_width / self.image_width
        self.place_image()

    def place_image(self):
        self.image_output.delete('all')
        pil_image = self.cv2_to_pil(self.image)
        pil_image.thumbnail((int(self.image_width), int(self.image_height)), Image.LANCZOS)
        self.image_tk = self.pil_to_tk(pil_image)
        self.image_output.create_image(self.canvas_width / 2, self.canvas_height / 2, image=self.image_tk)

    def pil_to_tk(self, pil_image):
        return ImageTk.PhotoImage(pil_image)

    def cv2_to_pil(self, cv2_image):
        return Image.fromarray(cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB))

    def pil_to_cv2(self, pil_image):
        arr_image = np.array(pil_image)
        return cv2.cvtColor(arr_image, cv2.COLOR_RGB2BGR)

    def cv2_to_tk(self, image):
        pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        return ImageTk.PhotoImage(pil)

    def reset_params(self):
        self.image_params['position']['rotate'].set(ROTATE_DEFAULT)
        self.image_params['position']['flip'].set(FLIP_OPTIONS[0])
        self.image_params['color']['vibrance'].set(VIBRANCE_DEFAULT)
        self.image_params['color']['brightness'].set(BRIGHTNESS_DEFAULT)
        self.image_params['color']['grayscale'].set(GRAYSCALE_DEFAULT)
        self.image_params['color']['invert'].set(INVERT_DEFAULT)
        self.image_params['effect']['blur'].set(BLUR_DEFAULT)
        self.image_params['effect']['contrast'].set(CONTRAST_DEFUALT)
        self.image_params['convolution']['four_edge'].set(FOUR_WAY_EDGE_DEFAULT)
        self.image_params['convolution']['blur'].set(BLUR_2_DEFAULT)
        self.image_params['convolution']['point'].set(POINT_EDGE_DEFAULT)
        self.image_params['convolution']['sharpen'].set(SHARPEN_DEFAULT)
        self.image_params['convolution']['shadow_floor'].set(SHARPEN_DEFAULT)
        self.image_params['convolution']['highlight_ceiling'].set(HIGHLIGHT_CEILING_DEFAULT)

    def set_selection(self, mask=None):
        if mask is None:
            self.mask = None
            self.original = self.image
            self.reset_params()
        else:
            self.original = self.image
            self.mask = mask

    def apply_mask(self, manipulated_image):
        mask = self.mask[:, :, :1]
        result_image = np.where(mask == 255, manipulated_image, self.image) 
        return result_image

    # image manipulation
    def manipulate_image(self, params):
        self.image_params = params
        self.image = self.original

        # get all vars
        rotate_angle = self.image_params['position']['rotate'].get()
        flip = self.image_params['position']['flip'].get()
        vibrance = self.image_params['color']['vibrance'].get()
        brightness = self.image_params['color']['brightness'].get()
        grayscale = self.image_params['color']['grayscale'].get()
        invert = self.image_params['color']['invert'].get()
        blur = self.image_params['effect']['blur'].get()
        contrast = self.image_params['effect']['contrast'].get()
        four_edge = self.image_params['convolution']['four_edge'].get()
        blur2 = self.image_params['convolution']['blur'].get()
        point_edge = self.image_params['convolution']['point'].get()
        sharpen = self.image_params['convolution']['sharpen'].get()
        shadow_floor = self.image_params['convolution']['shadow_floor'].get()
        highlight_ceiling = self.image_params['convolution']['highlight_ceiling'].get()

        # manipulation functions
        self.manipulate_position(rotate_angle, flip)
        self.manipulate_colors(brightness, vibrance, grayscale, invert)
        self.manipulate_effects(contrast, blur)
        self.manipulate_basic_convolutions(four_edge, blur2, sharpen, point_edge, shadow_floor, highlight_ceiling)
        self.place_image()

    def manipulate_position(self, rotate, flip):
        pil_image = self.cv2_to_pil(self.image)
        if flip != FLIP_OPTIONS[0]:
            if flip == "X":
                pil_image = ImageOps.mirror(pil_image)
            elif flip == 'Y':
                pil_image = ImageOps.flip(pil_image)
            elif flip == 'Both':
                pil_image = ImageOps.mirror(pil_image)
                pil_image = ImageOps.flip(pil_image)
        if rotate != ROTATE_DEFAULT:
            pil_image = pil_image.rotate(rotate, resample=Image.BICUBIC)
        manipulated_image = self.pil_to_cv2(pil_image)
        if self.mask is not None:
            manipulated_image = self.apply_mask(manipulated_image)
        self.image = manipulated_image

    def manipulate_colors(self, brightness, vibrance, grayscale, invert):
        pil_image = self.cv2_to_pil(self.image)
        if brightness != BRIGHTNESS_DEFAULT:
            brightness_enhancer = ImageEnhance.Brightness(pil_image)
            pil_image = brightness_enhancer.enhance(brightness)
        if vibrance != VIBRANCE_DEFAULT:
            vibrance_enhancer = ImageEnhance.Color(pil_image)
            pil_image = vibrance_enhancer.enhance(vibrance)
        if grayscale:
            pil_image = ImageOps.grayscale(pil_image)
        if invert:
            pil_image = ImageOps.invert(pil_image)
        manipulated_image = self.pil_to_cv2(pil_image)
        if self.mask is not None:
            manipulated_image = self.apply_mask(manipulated_image)
        self.image = manipulated_image

        # convolution stuff

    def convolve(self, image, kernel):
        return cv2.filter2D(image, -1, kernel)

    def merge(self, one, two, alpha=0.5, beta=0.5):
        return cv2.addWeighted(one, alpha, two, beta, 0)

    def four_way_edge_detection(self, image):
        kernel1 = np.array([[-2, -1, 0],
                            [-1, 0, 1],
                            [0, 1, 2]])
        kernel2 = np.array([[2, 1, 0],
                            [1, 0, -1],
                            [0, -1, -2]])
        kernel3 = np.array([[0, 1, 2],
                            [-1, 0, 1],
                            [-2, -1, 0]])
        kernel4 = np.array([[0, -1, -2],
                            [1, 0, -1],
                            [2, 1, 0]])
        one = self.convolve(image, kernel1)
        two = self.convolve(image, kernel2)
        three = self.convolve(image, kernel3)
        four = self.convolve(image, kernel4)
        merged_1 = self.merge(one, four)
        merged_2 = self.merge(three, two)
        return self.merge(merged_1, merged_2)

    def blur(self, image):
        blurr_kernel = np.array([[0.003, 0.013, 0.022, 0.013, 0.003],
                                 [0.013, 0.060, 0.098, 0.060, 0.013],
                                 [0.022, 0.098, 0.162, 0.098, 0.022],
                                 [0.013, 0.060, 0.098, 0.060, 0.013],
                                 [0.003, 0.013, 0.022, 0.013, 0.003]])
        return self.convolve(image, blurr_kernel)

    def point_edge(self, image):
        edge = np.array([[-1.5, -1.5, -1.5],
                         [-1.5, 11, -1.5],
                         [-1.5, -1.5, -1.5]])
        return self.convolve(image, edge)

    def sharpen(self, image):
        sharpen_kernel = np.array([[0, -1, 0],
                                   [-1, 5, -1],
                                   [0, -1, 0]])
        return self.convolve(image, sharpen_kernel)

    def floor_shadows(self, val, image):
        low = np.where(image < val)
        image[low] = image[low] * 0.5
        return image

    def ceiling_highlights(self, val, image):
        high = np.where(image > val)
        image[high] = np.where(image[high] * 1.5 < 255, image[high] * 1.5, 255)
        return image

    def manipulate_basic_convolutions(self, four_edge, blur, sharpen, point_edge, shadow_floor, highlight_ceiling):
        manipulated_image = self.image.copy()
        if four_edge:
            manipulated_image = self.four_way_edge_detection(manipulated_image)
        if blur:
            manipulated_image = self.blur(manipulated_image)
        if point_edge:
            manipulated_image = self.point_edge(manipulated_image)
        if sharpen:
            manipulated_image = self.sharpen(manipulated_image)
        if shadow_floor != SHADOW_FLOOR_DEFAULT:
            manipulated_image = self.floor_shadows(shadow_floor, manipulated_image)
        if highlight_ceiling != HIGHLIGHT_CEILING_DEFAULT:
            manipulated_image = self.ceiling_highlights(highlight_ceiling, manipulated_image)
        if self.mask is not None:
            manipulated_image = self.apply_mask(manipulated_image)
        self.image = manipulated_image

    def manipulate_effects(self, contrast, blur):
        pil_image = self.cv2_to_pil(self.image)
        if blur != BLUR_DEFAULT:
            pil_image = pil_image.filter(ImageFilter.GaussianBlur(blur))
        if contrast != BLUR_DEFAULT:
            pil_image = pil_image.filter(ImageFilter.UnsharpMask(contrast))
        manipulated_image = self.pil_to_cv2(pil_image)
        if self.mask is not None:
            manipulated_image = self.apply_mask(manipulated_image)
        self.image = manipulated_image


class SecondaryImageDisplay(ImageDisplay):
    def __init__(self, parent, image, params):
        super().__init__(parent, image, params)
        self.close_button = CloseOutput(self, self.close_edit)
        self.exists = ctk.IntVar(value=1)

    def close_edit(self):
        if tk.messagebox.askokcancel("Close", "Do you want to continue?"):
            self.close_button.place_forget()
            self.image_output.pack_forget()
            self.exists.set(0)
