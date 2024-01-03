# solve perspective distortion and crop out the ROI
import cv2
import numpy as np


def trape(image, p1, p2, p3, p4):

    pts1 = np.float32([p1, p2, p3, p4]) # vertices of the ROI
    pts2 = np.float32([[0, 0], [image.shape[1], 0], [0, image.shape[0]], [image.shape[1], image.shape[0]]])

    # cal transformation matrix and perform transform
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    trapezoid = cv2.warpPerspective(image, matrix, (image.shape[1], image.shape[0]))

    return trapezoid

if __name__ == "__main__":
    
    image = cv2.imread('./test_images/sample.png')
    p1 = ...
    p2 = ...
    p3 = ...
    p4 = ...
    trapezoid = trape(image, p1, p2, p3, p4)
    cv2.namedWindow('Trapezoid', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Trapezoid', 640, 480)
    cv2.imshow('Trapezoid', trapezoid)
    cv2.waitKey(0)
    cv2.destroyAllWindows()