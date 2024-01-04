# solve perspective distortion and crop out the ROI
import cv2
import numpy as np


def trape(image, p1, p2, p3, p4):

    pts1 = np.float32([p1, p2, p3, p4]) # vertices of the ROI
    pts2 = np.float32([[0, 0], [image.shape[1], 0], [image.shape[1], image.shape[0]], [0, image.shape[0]]])

    # cal transformation matrix and perform transform
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    trapezoid = cv2.warpPerspective(image, matrix, (image.shape[1], image.shape[0]))

    return trapezoid

if __name__ == "__main__":
    
    image = cv2.imread('./test_images/sample.png')  # 替换为你的图片路径
    print(image.shape)
    p1 = [420, 58]
    p2 = [2048, 39]
    p3 = [2148, 1348]
    p4 = [313, 1329]
    trapezoid = trape(image, p1, p2, p3, p4)
    cv2.namedWindow('Trapezoid', cv2.WINDOW_NORMAL)
    cv2.imshow('Trapezoid', trapezoid)
    cv2.waitKey(0)
    cv2.destroyAllWindows()