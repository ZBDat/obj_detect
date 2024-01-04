import cv2
import os
import numpy as np
from matplotlib import pyplot as plt
from distortion import trape


def edgeDetect(image):
    
    # blurring filters to be chosen:
    # image = cv2.blur(image, 5)
    # image = cv2.GaussianBlur(image, (5, 5), 0)
    # image = cv2.medianBlur(image, 5)
    # image = cv2.bilateralFilter(image, 7, sigmaColor=50, sigmaSpace=50)
    # image = cv2.fastNlMeansDenoising(image, None, h=20, templateWindowSize=5, searchWindowSize=31)
    
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 91, 30)
    kernel = np.ones((3,3), np.uint8)
    kernel_2 = np.ones((5,5), np.uint8)
    # img1 = cv2.erode(img1, kernel, iterations=1)
    opening = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, 2)
    dilate = cv2.dilate(opening, kernel_2, 1)
    image = cv2.medianBlur(dilate, 5)

    # canny
    v = np.median(image)
    sigma = 0.25
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edges = cv2.Canny(image, threshold1=lower, threshold2=upper)
    
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # find max contour
    max_length = 0
    max_area = 0
    max_contour = None
    for contour in contours:
        length = cv2.arcLength(contour, True)
        if length > max_length:
            max_length = length
            max_contour = contour
    
    return max_length, max_contour


if __name__ == "__main__":
    path = '...'
    files = os.listdir(path)
    for file in files:
        ori_image = cv2.imread(os.path.join(path, file))
        p1 = [601, 136]
        p2 = [2238, 117]
        p3 = [2336, 1400]
        p4 = [499, 1405]
        image = trape(ori_image, p1, p2, p3, p4)
        # image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # image = cv2.convertScaleAbs(image, alpha=1.2)
        max_length, max_contour = edgeDetect(image)

        if max_contour is not None:
            print(file, "max length of contours:", max_length)
            # Draw the max contour on the image
            image_with_contour = cv2.drawContours(image, [max_contour], -1, (0, 255, 0), 2)
            plt.imshow(image_with_contour)
            plt.title('Image with Contour')
            plt.show()
            