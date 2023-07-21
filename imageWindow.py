import customtkinter as ctk
import tkinter as tk
import cv2
from PIL import Image, ImageTk, ImageOps, ImageEnhance, ImageFilter
from imageWidgets import *
import numpy as np


class ImageWindow(ctk.CTkToplevel):
    def __init__(self, parent, params, image):
        super().__init__(parent)
        self.title("Analog Intelligence")
        self.geometry("1700x1300+600+100")
        self.protocol('WM_DELETE_WINDOW', self.close_edit)
        self.minsize(800, 500)
        self.image_output = ImageOutput(self, self.resize_image)
        self.close_button = CloseOutput(self, self.close_edit)
        self.exists = ctk.IntVar(value = 1)

        self.original = image
        self.image = self.original
        self.image_params = params

        
        # canvas data
        self.image_width = 0
        self.image_height = 0
        self.canvas_width = 0
        self.canvas_height = 0

        
        self.image_height, self.image_width = self.image.shape[:2]
        self.image_ratio = self.image_width / self.image_height
        
        

    def close_edit(self):
        if tk.messagebox.askokcancel("Close", "Do you want to continue?"):
            self.close_button.place_forget()
            self.image_output.pack_forget()
            self.exists.set(0)

    def get_image(self):
        return self.image


    def resize_image(self, event):
        canvas_ratio = event.width / event.height

        self.canvas_width = event.width
        self.canvas_height = event.height

        if canvas_ratio > self.image_ratio:
            self.image_height = event.height
            self.image_width = self.image_height * self.image_ratio
        else:
            self.image_width = event.width
            self.image_height = self.image_width/self.image_ratio
        self.place_image()

    def place_image(self):
        self.image_output.delete('all')
        resized_image = cv2.resize(self.image, (int(self.image_width), int(self.image_height)))
        self.image_tk = self.cv2_to_tk(resized_image)
        self.image_output.create_image(self.canvas_width/2, self.canvas_height/2, image = self.image_tk)

    
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




 # image manipulation
    def manipulate_image(self, params):
        self.image_params = params
        self.image = self.original

        #get all vars
        rotate_angle = self.image_params['position']['rotate'].get()
        flip = self.image_params['position']['flip'].get()
        vibrance = self.image_params['color']['vibrance'].get()
        brightnes = self.image_params['color']['brightness'].get()
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
        #manpulation functions
        self.manipulate_position(rotate_angle, flip)
        self.manipulate_colors(brightnes, vibrance, grayscale, invert)
        self.manipulate_effects(contrast, blur)
        self.manipulate_basic_convolutions(four_edge, blur, sharpen, point_edge, shadow_floor, highlight_ceiling)
        self.place_image()    

    def manipulate_position(self, rotate, flip):

        height, width = self.image.shape[:2]
        height, width = int(height), int(width)
        center = (width // 2, height // 2)
        
        #flip
        if (flip != FLIP_OPTIONS[0]):
            if flip == "X":
                pil_image = self.cv2_to_pil(self.image)
                pil_image = ImageOps.mirror(pil_image)
                self.image = self.pil_to_cv2(pil_image)
            elif flip == 'Y':
                pil_image = self.cv2_to_pil(self.image)
                pil_image = ImageOps.flip(pil_image)
                self.image = self.pil_to_cv2(pil_image)
            elif flip == 'Both':
                pil_image = self.cv2_to_pil(self.image)
                pil_image = ImageOps.mirror(pil_image)
                pil_image = ImageOps.flip(pil_image)
                self.image = self.pil_to_cv2(pil_image)

        #rotate
        if (rotate != ROTATE_DEFAULT):
            rotation_matrix = cv2.getRotationMatrix2D(center, rotate, 1.0)
            self.image = cv2.warpAffine(self.image, rotation_matrix, (width, height))

    def manipulate_colors(self, brightnes, vibrance, grayscale, invert):
        pil_image = self.cv2_to_pil(self.image)
        if (brightnes != BRIGHTNESS_DEFAULT):
            brightness_enhancer = ImageEnhance.Brightness(pil_image)
            pil_image = brightness_enhancer.enhance(brightnes)
        if (vibrance != VIBRANCE_DEFAULT):
            vibrance_enhancer = ImageEnhance.Color(pil_image)
            pil_image = vibrance_enhancer.enhance(vibrance)
        if (grayscale):
            pil_image = ImageOps.grayscale(pil_image)
        if (invert):
            pil_image = ImageOps.invert(pil_image)
        self.image = self.pil_to_cv2(pil_image) 

    #convolution stuff
    def convolve(self, image, kernel):
        return cv2.filter2D(image, -1, kernel)

    def merge(self, one, two, alpha = 0.5, beta = 0.5):
        return cv2.addWeighted(one, alpha, two, beta, 0)

    def four_way_edge_detection(self):
        image = self.image
        kernel1 = np.array([[-2,-1,0],
                                [-1,0,1],
                                [0,1,2]])
        kernel2 = np.array([[2,1,0],
                                [1,0,-1],
                                [0,-1,-2]])
        kernel3 = np.array([[0,1,2],
                                [-1,0,1],
                                [-2,-1,0]])
        kernel4 = np.array([[0,-1,-2],
                                [1,0,-1],
                                [2,1,0]])
        one = self.convolve(image, kernel1)
        two = self.convolve(image, kernel2)
        three = self.convolve(image, kernel3)
        four = self.convolve(image, kernel4)
        merged_1 = self.merge(one, four)
        merged_2 = self.merge(three, two)
        self.image = self.merge(merged_1, merged_2) 

    def blur(self):
        image = self.image
        blurr_kernel = np.array([[0.003,0.013,0.022,0.013,0.003],
                            [0.013,0.060,0.098,0.060,0.013],
                            [0.022,0.098,0.162,0.098,0.022],
                            [0.013,0.060,0.098,0.060,0.013],
                            [0.003,0.013,0.022,0.013,0.003]])
        self.image =  self.convolve(image, blurr_kernel)

    def point_edge(self):
        image = self.image
        edge = np.array([[-1.5,-1.5,-1.5],
                            [-1.5,11,-1.5],
                            [-1.5,-1.5,-1.5]]) 
        self.image = self.convolve(image, edge)

    def sharpen(self):
        image = self.image
        sharpen_kernel = np.array([[0,-1,0],
                            [-1,5,-1],
                            [0,-1,0]]) 
        self.image = self.convolve(image, sharpen_kernel)

    def floor_shadows(self, val):
        image = self.image
        low = np.where(image < val)
        image[low] = image[low] * 0.5
        self.image = image

    def ceiling_highlights(self, val):
        image = self.image
        high = np.where(image > val)
        image[high] = np.where(image[high] * 1.5 < 255, image[high] * 1.5, 255)
        self.image = image

    def manipulate_basic_convolutions(self, four_edge, blur, sharpen, point_edge, shadow_floor, highlight_ceiling):
        if (four_edge):
            self.four_way_edge_detection()
        if (blur):
            self.blur()
        if (point_edge):
            self.point_edge()
        if (sharpen):
            self.sharpen()
        if (shadow_floor != SHADOW_FLOOR_DEFAULT):
            self.floor_shadows(shadow_floor)
        if (highlight_ceiling != HIGHLIGHT_CEILING_DEFAULT):
            self.ceiling_highlights(highlight_ceiling)

    def manipulate_effects(self, contrast, blur):
        pil_image = self.cv2_to_pil(self.image)
        if (blur != BLUR_DEFAULT): 
            pil_image = pil_image.filter(ImageFilter.GaussianBlur(blur))
        if (contrast != BLUR_DEFAULT):
            pil_image = pil_image.filter(ImageFilter.UnsharpMask(contrast))

        self.image = self.pil_to_cv2(pil_image) 

    