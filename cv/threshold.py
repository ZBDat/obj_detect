# test script for the best params setting of preprocess
import cv2
import os
import itertools  
import numpy as np  


if __name__ == "__main__":
    positive_path = './pics/Crop/OK'
    negative_path = './pics/Crop/Test'


    img1 = cv2.imread(os.path.join('.','20231208_110300.png'), 0)
    img1 = cv2.convertScaleAbs(img1, alpha=1.8)
    # img1 = cv2.GaussianBlur(img1, (5, 5), 0)
    img1 = cv2.medianBlur(img1, 3)
    img1 = cv2.adaptiveThreshold(img1, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 91, 30)
    kernel = np.ones((3,3), np.uint8)
    kernel_2 = np.ones((5,5), np.uint8)
    # img1 = cv2.erode(img1, kernel, iterations=1)
    opening = cv2.morphologyEx(img1, cv2.MORPH_OPEN, kernel, 2)
    dilate = cv2.dilate(opening, kernel_2, 1)
    res = cv2.medianBlur(dilate, 5)
    ss = np.hstack((img1, res))
    cv2.imwrite('thresholdN.png', ss)