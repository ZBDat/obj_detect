# 示例：解析相应
import requests
import cv2
import numpy as np


url = 'http://localhost:5000/yolo_result'

response = requests.get(url)

if response.status_code == 200:
    value = response.headers.get('Result')

    image_as_np = np.frombuffer(response.content, dtype=np.uint8)
    image = cv2.imdecode(image_as_np, cv2.IMREAD_COLOR)

    cv2.imshow('Received Image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    print(f'Received boolean value: {value}')
else:
    print(f'Failed to retrieve data. Status code: {response.status_code}')