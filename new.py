import cv2
import numpy as np

def transform_image(points, image):
    # 获取四个点的坐标
    pts1 = np.float32(points)
    
    # # 定义转换后的长方形的宽度和高度
    # width = 640
    # height = 480
    
    # 定义转换后的长方形的四个角点坐标
    pts2 = np.float32([[0, 0], [image.shape[1], 0], [image.shape[1], image.shape[0]], [0, image.shape[0]]])
    
    # 计算透视变换矩阵
    M = cv2.getPerspectiveTransform(pts1, pts2)
    
    # 进行透视变换
    transformed_image = cv2.warpPerspective(image, M, (image.shape[1], image.shape[0]))
    
    return transformed_image
    
    
# 鼠标回调函数
def click_event(event, x, y, flags, params):
    global points
    # 检查事件是否为左键点击
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f'Clicked Position: X = {x}, Y = {y}')
        cv2.circle(img, (x, y), 3, (255, 0, 0), -1)
        cv2.imshow('image', img)
        points.append((x, y))
        if len(points) == 4:
            new_image = transform_image(points, img)
            cv2.imwrite('new_image.png', new_image)

# 读取图片
img = cv2.imread('./test_images/N1.png')  # 替换为你的图片路径
cv2.namedWindow('image', cv2.WINDOW_NORMAL)
cv2.imshow('image', img)

# 设置鼠标回调函数
points = []
cv2.setMouseCallback('image', click_event)

cv2.waitKey(0)
cv2.destroyAllWindows()