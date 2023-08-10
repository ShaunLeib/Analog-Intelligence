import numpy as np
import cv2
from abc import ABC, abstractmethod
from skimage.draw import line_aa


class Selection(ABC):
    def __init__(self, image_window, done):
        self.last_x = 0
        self.last_y = 0
        self.canvasx = 0
        self.canvasy = 0
        self.image_window = image_window
        self.canvas = image_window.get_current_canvas()
        self.height, self.width = image_window.get_current_original_image_size()
        self.mask = self.create_mask()
        self.image = image_window.get_current_image()
        self.vert_start = 0
        self.vert_end = 0
        self.vert_ratio = 0
        self.horiz_start = 0
        self.horiz_end = 0
        self.horiz_ratio = 0
        self.done = done

    def create_mask(self):
        return np.ones((self.height, self.width))

    def merge_selection_image(self, mask):
        mask_3d = np.stack([mask] * 3, axis = -1)
        image = self.image.copy()
        bitwise = cv2.bitwise_and(image, mask_3d)
        self.image_window.add_secondary_image(bitwise, ())
        self.mask = self.create_mask()
        self.canvas.delete("selection")
        return bitwise

    def make_3d(self):
        return (self.mask * 255).astype(np.uint8)

    def reset_params(self):
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.last_y = 0
        self.last_x = 0
        self.canvasy = 0
        self.canvasx = 0

    def align_x(self, x):
        return int((x - self.horiz_start) * self.horiz_ratio)

    def align_y(self, y):
        return int((y - self.vert_start) * self.vert_ratio)

    def fill_bounds(self, image_in):
        th, im_th = cv2.threshold(image_in, 200, 255, cv2.THRESH_BINARY)
        im_floodfill = im_th.copy()
        h, w = im_th.shape[:2]
        mask = np.zeros((h + 2, w + 2), np.uint8)
        cv2.floodFill(im_floodfill, mask, (0, 0), (0, 0, 0))
        return im_floodfill

    def init_selection(self):
        image_height, image_width = self.image_window.get_current_image_size()
        vertical, horizontal = self.image_window.get_current_canvas_difference()
        self.vert_start = vertical
        self.vert_end = vertical + image_height
        self.horiz_start = horizontal
        self.horiz_end = horizontal + image_width
        self.vert_ratio, self.horiz_ratio = self.image_window.get_current_ratios()

    def get_x_and_y(self, event):
        self.last_x = self.align_x(event.x)
        self.last_y = self.align_y(event.y)
        self.canvasy = event.y
        self.canvasx = event.x

    def select(self):
        self.init_selection()

    @abstractmethod
    def draw(self, event):
        pass

    @abstractmethod
    def stop(self, event):
        pass

    def final(self):
        self.reset_params()
        self.done.set(1)


class Rectangle(Selection):
    def __init__(self, image_window, done):
        super().__init__(image_window, done)

    def select(self):
        super().select()
        self.canvas.create_rectangle((0, 0, 1, 1), outline="red", width=2, tags=("selection", "rectangle"))
        self.canvas.bind("<Button-1>", self.get_x_and_y)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop)

    def draw(self, event):
        if self.canvasx < self.horiz_end and self.canvasx >= self.horiz_start and self.canvasy < self.vert_end and self.canvasy >= self.vert_start and event.x < self.horiz_end and event.x >= self.horiz_start and event.y < self.vert_end and event.y >= self.vert_start:
            self.canvas.coords("rectangle", self.canvasx, self.canvasy, event.x, event.y)

    def stop(self, event):
        if self.canvasx < self.horiz_end and self.canvasx >= self.horiz_start and self.canvasy < self.vert_end and self.canvasy >= self.vert_start and event.x < self.horiz_end and event.x >= self.horiz_start and event.y < self.vert_end and event.y >= self.vert_start:
            x0, y0, x1, y1 = self.canvas.coords("rectangle")
            x0 = self.align_x(x0)
            y0 = self.align_y(y0)
            x1 = self.align_x(x1)
            y1 = self.align_y(y1)
            self.mask = cv2.rectangle(self.mask, (x0, y0), (x1, y1), (0, 0, 0), -1)
            self.final()

    def final(self):
        super().final()
        selection = self.make_3d()
        selection = cv2.bitwise_not(selection)
        self.merge_selection_image(selection)


class Circle(Selection):
    def __init__(self, image_window, done):
        super().__init__(image_window, done)

    def select(self):
        super().select()
        self.canvas.create_oval((0, 0, 1, 1), outline="red", width=2, tags=("selection", "circle"))
        self.canvas.bind("<Button-1>", self.get_x_and_y)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop)

    def draw(self, event):
        if self.canvasx < self.horiz_end and self.canvasx >= self.horiz_start and self.canvasy < self.vert_end and self.canvasy >= self.vert_start and event.x < self.horiz_end and event.x >= self.horiz_start and event.y < self.vert_end and event.y >= self.vert_start:
            self.canvas.coords("circle", self.canvasx, self.canvasy, event.x, event.y)

    def stop(self, event):
        if self.canvasx < self.horiz_end and self.canvasx >= self.horiz_start and self.canvasy < self.vert_end and self.canvasy >= self.vert_start and event.x < self.horiz_end and event.x >= self.horiz_start and event.y < self.vert_end and event.y >= self.vert_start:
            x0, y0, x1, y1 = self.canvas.coords("circle")
            x0 = self.align_x(x0)
            y0 = self.align_y(y0)
            x1 = self.align_x(x1)
            y1 = self.align_y(y1)
            vertical = int((y1 - y0) / 2)
            horizontal = int((x1 - x0) / 2)
            center = (horizontal + x0, vertical + y0)
            self.mask = cv2.ellipse(self.mask, center, (horizontal, vertical), 0, 0, 360, (0,0,0), -1)
            self.final()

    def final(self):
        super().final()
        selection = self.make_3d()
        selection = cv2.bitwise_not(selection)
        self.merge_selection_image(selection)


class Free(Selection):
    def __init__(self, image_window, done):
        super().__init__(image_window, done)

    def select(self):
        super().select()
        self.canvas.bind("<Button-1>", self.get_x_and_y)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.free_final)

    def draw(self, event):
        if self.canvasx < self.horiz_end and self.canvasx >= self.horiz_start and self.canvasy < self.vert_end and self.canvasy >= self.vert_start and event.x < self.horiz_end and event.x >= self.horiz_start and event.y < self.vert_end and event.y >= self.vert_start:
            x = self.align_x(event.x)
            y = self.align_y(event.y)
            self.canvas.create_line((self.canvasx, self.canvasy, event.x, event.y), fill='red', width=2, tags=("selection", "free"))
            rr, cc, val = line_aa(self.last_y, self.last_x, y, x)
            self.mask[rr, cc] = val * 0
            self.last_x = x
            self.last_y = y
            self.canvasx = event.x
            self.canvasy = event.y

    def stop(self, event):
        raise NotImplementedError("Stop method is not needed for free selection")

    def free_final(self, _event):
        super().final()
        selection = self.make_3d()
        filled_mask = self.fill_bounds(selection)
        self.merge_selection_image(filled_mask)

    def final(self):
        raise NotImplementedError("Use free_final instead of final for the free class")


class Polygon(Selection):
    def __init__(self, image_window, done):
        super().__init__(image_window, done)

    def select(self):
        super().select()
        self.canvas.bind_all("<Return>", self.stop)
        self.canvas.bind("<Button-1>", self.get_x_and_y)

    def get_x_and_y(self, event):
        super().get_x_and_y(event)
        self.canvas.create_line((self.canvasx, self.canvasy, event.x, event.y), fill='red', width=2, tags=("selection", "poly"))
        self.canvas.bind("<Motion>", self.draw)
        self.canvas.bind("<Button-1>", self.poly_endpoint)

    def draw(self, event):
        if self.canvasx < self.horiz_end and self.canvasx >= self.horiz_start and self.canvasy < self.vert_end and self.canvasy >= self.vert_start and event.x < self.horiz_end and event.x >= self.horiz_start and event.y < self.vert_end and event.y >= self.vert_start:
            self.canvas.coords("poly", self.canvasx, self.canvasy, event.x, event.y)

    def poly_endpoint(self, event):
        if self.canvasx < self.horiz_end and self.canvasx >= self.horiz_start and self.canvasy < self.vert_end and self.canvasy >= self.vert_start and event.x < self.horiz_end and event.x >= self.horiz_start and event.y < self.vert_end and event.y >= self.vert_start:
            self.canvas.create_line((self.canvasx, self.canvasy, event.x, event.y), fill="red", width=2, tags=("selection", 'poly_final'))
            self.canvasx = event.x
            self.canvasy = event.y

    def stop(self, event):
        self.canvas.unbind("<Motion>")
        self.canvas.unbind_all("<Return>")
        self.final()

    def get_poly_endpoints(self):
        tags = self.canvas.find_withtag("poly_final")
        coords = []
        for tag in tags:
            coord = [self.align_x(val) if (i % 2 == 0) else self.align_y(val) for i, val in enumerate(self.canvas.coords(tag))]
            coords.append(coord)
        coords = np.array(coords, np.int32)
        coords = coords.reshape((-1, 1, 2))
        return coords

    def final(self):
        super().final()
        coords = self.get_poly_endpoints()
        self.mask = cv2.polylines(self.mask, [coords], False, (0, 0, 0), 2)
        selection = self.make_3d()
        filled_mask = self.fill_bounds(selection)
        self.merge_selection_image(filled_mask)