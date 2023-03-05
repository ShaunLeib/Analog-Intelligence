import cv2 as cv
import numpy as np


def rotate(image, angle):
    center = (image.shape[1]//2, image.shape[0]//2)
    matrix = cv.getRotationMatrix2D(center, angle, 1.0)
    return cv.warpAffine(image, matrix, (image.shape[1], image.shape[0]))

def region_of_interest(image, height_start, height_end, width_start, width_end):
    return image[height_start:height_end, width_start:width_end]


def convolution(image, kernel):
    return cv.filter2D(image, -1, kernel)

def split_image_by_color(image):
    B,G,R= cv.split(image)
    cv.imshow("B",B)
    cv.imshow("G",G)
    cv.imshow("R",R)
    cv.waitKey(0)
    cv.destroyAllWindows()

def merge(one, two, alpha = 0.5, beta = 0.5):
    return cv.addWeighted(one, alpha, two, beta, 0)

def shadow_floor(image):
    low = np.where(image < 40)
    image[low] = image[low] * 0.5
    return image

def highlight_ceiling(image):
    high = np.where(image > 100)
    image[high] = image[high] * 1.5
    return image

def four_way_edge_detection(image):
    test_kernel = np.array([[-2,-1,0],
                            [-1,0,1],
                            [0,1,2]])
    test2_kernel = np.array([[2,1,0],
                             [1,0,-1],
                            [0,-1,-2]])
    test3_kernel = np.array([[0,1,2],
                             [-1,0,1],
                            [-2,-1,0]])
    test4_kernel = np.array([[0,-1,-2],
                             [1,0,-1],
                            [2,1,0]])
    test = convolution(image, test_kernel)
    test2 = convolution(image, test2_kernel)
    test3 = convolution(image, test3_kernel)
    test4 = convolution(image, test4_kernel)
    merged_1 = merge(test, test4)
    merged_2 = merge(test3, test2)
    return merge(merged_1, merged_2)

def sharpen(image):
    sharpen_kernel = np.array([[0,-1,0],
                          [-1,5,-1],
                          [0,-1,0]]) 
    return convolution(image, sharpen_kernel)

def blurr(image):
    blurr_kernel = np.array([[0.003,0.013,0.022,0.013,0.003],
                          [0.013,0.060,0.098,0.060,0.013],
                          [0.022,0.098,0.162,0.098,0.022],
                          [0.013,0.060,0.098,0.060,0.013],
                          [0.003,0.013,0.022,0.013,0.003]])
    return convolution(image, blurr_kernel)

def static_edge(image):
    edge = np.array([[-1.5,-1.5,-1.5],
                          [-1.5,11,-1.5],
                          [-1.5,-1.5,-1.5]]) 
    return convolution(image, edge)




    

def main():
    image = cv.imread("./colorTest.jpg") # ,0 param to grayscale
    h,w = image.shape[:2]
    B,G,R = cv.split(image)
    print("shape; ", image.shape)
    print(f"height: {h}, w: {w}")
    cv.imshow("og", image)

    #other edge
    other_edge_image = static_edge(image)
    other_edge_image = shadow_floor(other_edge_image)
    other_edge_image = highlight_ceiling(other_edge_image)
    cv.imshow("other", other_edge_image)

    #total edge
    merge_total = four_way_edge_detection(image)   
    floored = shadow_floor(merge_total)
    floored = highlight_ceiling(floored)
    cv.imshow("floored", floored)
    final = merge(image, floored, alpha=0.2, beta=0.8) #needs brightness/exposure increase. Mess w/ shadows & highlights. Staturation increase
    brightness = cv.convertScaleAbs(final, alpha=2, beta = 20)
    cv.imshow("brightness", brightness)

    #color spaces
    B_edge = four_way_edge_detection(B)
    G_edge = static_edge(G)
    R_edge = four_way_edge_detection(R)
    bgr_merge = cv.merge([B_edge,G_edge,R_edge])
    bgr_merge = shadow_floor(bgr_merge)
    bgr_merge = highlight_ceiling(bgr_merge)
    cv.imshow("BGR", bgr_merge)



    


    # cv.imshow("edge", edge)
    # cv.imshow("blurr", blurr)
    # cv.imshow("sharpen", sharpen)
    cv.waitKey(0)
    cv.destroyAllWindows()
    

    

if __name__ == "__main__":
    main()