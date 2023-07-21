import customtkinter as ctk
import tkinter as tk
import cv2
from PIL import Image, ImageTk, ImageOps, ImageEnhance, ImageFilter
from imageWidgets import *
import numpy as np
from imageWindow import ImageWindow

class SecondaryImageWindow(ImageWindow):
    def __init__(self, parent, params, image):
        super().__init__(parent, params, image)
        self.merge_button = ctk.CTkButton(self, text = "Merge", command = self.merge)
        self.merge_button.pack(pady = 10)

    def merge(self):
        pass