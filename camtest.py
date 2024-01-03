"""
Test for the cam communication function.
"""

import cv2
import requests
import numpy as np


def get_frames(stream_url):
    with requests.get(stream_url, stream=True) as r:
        # 确保请求成功
        if r.status_code == 200:
            bytes_buffer = b''
            for chunk in r.iter_content(chunk_size=1024):
                bytes_buffer += chunk
                a = bytes_buffer.find(b'\xff\xd8')  # JPEG 开始
                b = bytes_buffer.find(b'\xff\xd9')  # JPEG 结束
                if a != -1 and b != -1:
                    jpg = bytes_buffer[a:b+2]  # JPEG 图像数据
                    bytes_buffer = bytes_buffer[b+2:]  # 移除处理过的数据
                    frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                    yield frame

def display_stream(stream_url):
    for frame in get_frames(stream_url):
        if frame is not None:
            cv2.imshow('Stream', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):  # 按 'q' 退出
                break
        else:
            break
    cv2.destroyAllWindows()

if __name__ == "__main__":
    stream_url = 'http://localhost:5000/video_feed'
    display_stream(stream_url)
