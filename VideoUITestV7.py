#单模式 双算法选项 多边形框选功能
#相机流放在后端 通过request请求访问
import cv2
import os
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import *
from PyQt5.QtGui import QFont, QMouseEvent, QPainter, QPaintEvent
import threading
import numpy as np
import sys
import time
from PIL import Image,ImageQt
import requests

class BoundarySelection(QDialog):
    crop_cor = pyqtSignal(list)
    def __init__(self, cur_img, width, height, parent = None):
        super().__init__(parent)
        self.width = width
        self.height = height
        self.cor = []


        layout = QVBoxLayout()
        #操作说明 左键选取 右键清除
        self.label = QLabel()
        self.label.setText("左键选取 右键清除")
        self.label.setFont(QFont("黑体", 40))
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        #显示框选图片
        self.canvas = Canvas(cur_img, width, height)
        layout.addWidget(self.canvas)
        self.canvas.mousePressEvent = self.canvas_mousePressEvent

        #完成按钮
        self.button = QPushButton('完成')
        self.button.setFixedSize(200,100)
        self.button.setFont(QFont("黑体", 40))
        self.button.setEnabled(False)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        self.setLayout(layout)

        #按下按钮 释放坐标信号与关闭窗口
        self.button.setEnabled(True)
        self.button.clicked.connect(self.emit_crop_info)
        #self.button.clicked.connect(self.accept)

    def canvas_mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.canvas.add_point(event.pos())
        elif event.button() == Qt.RightButton:
            self.canvas.clear_points()

    def emit_crop_info(self):
        for point in self.canvas.points:
            self.cor.append([point.x(),point.y()])
        print(self.cor)
        self.crop_cor.emit(self.cor)

    def closeEvent(self, event):
        # 断开与parent对象的所有信号槽连接
        #QObject.disconnect(self, None, self.parent(), None)s
        self.canvas.points.clear()
        self.canvas.painter.end()
        super().closeEvent(event)

class Canvas(QWidget):
    def __init__(self, cur_img, width, height):
        super().__init__()

        self.label = QLabel()
        self.img = Image.fromarray(cv2.cvtColor(cur_img, cv2.COLOR_BGR2RGB))
        self.img = ImageQt.ImageQt(self.img)
        self.pixmap = QPixmap.fromImage(self.img).scaled(width, height)
        # self.img = cv2.cvtColor(cur_img, cv2.COLOR_BGR2RGB)
        # self.qimage = QImage(self.img.data, width, height, QImage.Format_RGB888)
        # self.pixmap = QPixmap.fromImage(self.qimage)
        self.label.setPixmap(self.pixmap)
        self.label.setFixedSize(width, height)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        self.points = []

        self.paint_flag = False

    def add_point(self, point: QPoint):
        self.points.append(point)
        self.paint_flag = True
        # 请求更新绘制
        self.update()


    def clear_points(self):
        self.points.clear()
        self.painter.eraseRect(self.label.rect())
        self.label.setPixmap(self.pixmap)
        self.paint_flag = True
        # 请求更新绘制
        self.update()


    def paintEvent(self, event: QPaintEvent):
        if self.paint_flag:
            self.painter = QPainter(self.label.pixmap())
            if len(self.points) == 4:
                # 绘制四边形区域
                self.painter.setBrush(Qt.NoBrush)
                self.painter.setPen(Qt.red)

                self.painter.drawPolygon(*self.points)
            else:
                # 绘制已选择的点
                self.painter.setPen(Qt.red)
                for point in self.points:
                    self.painter.drawEllipse(point, 5, 5)
            self.paint_flag = False
            self.painter.end()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        uic.loadUi("MainWindowV2.ui",self)
        self.height = 480
        self.width = 640
        self.NG_count = 0
        self.crop_cor = None
        self.cur_frame = None
        #初始化显示界面
        #1)左框相机流
        #self.cap = cv2.VideoCapture(0)
        self.thread_cam = threading.Thread(target=self.video_show)
        self.thread_cam.daemon = True
        self.thread_cam.start()

        #2)右框暂时不显示信息
        self.DetectResult.setText("暂无结果")
        self.DetectResult.setFont(QFont("黑体", 40))
        self.DetectResult.setFixedSize(self.width, self.height)
        self.DetectResult.setAlignment(Qt.AlignCenter)

        #框选过程控制
        self.Select.clicked.connect(self.select_crop_boundary)
        #算法模式控制
        self.TakePic.clicked.connect(self.manualDetect)
        #

        self.show()

    def closeEvent(self,event):
        if self.thread_cam and self.thread_cam.is_alive():
            self.thread_cam.do_run = False
            # thread.join()方法是用来阻塞主线程，等待子线程完成其任务后再继续执行主线程
            self.thread_cam.join()
        self.dialog.reject()
        # self.cap.release()
        # cv2.destroyAllWindows()
        event.accept()

    def select_crop_boundary(self):
        #To Do：在左框上选取要截取的范围
        #更新按钮及显示状态

        self.dialog = BoundarySelection(self.cur_frame, self.width, self.height, self)

        self.dialog.crop_cor.connect(self.save_crop_cor)
        self.dialog.exec_()
        #self.dialog.deleteLater()
        #del dialog
        self.DetectResult.setText("框选完成")
        self.TakePic.setEnabled(True)

    def save_crop_cor(self, cor):
        self.crop_cor = cor
        print("Received cor", self.crop_cor)

    def get_frames(self, stream_url):
        with requests.get(stream_url, stream=True) as r:
            # stream=True以流的方式获取响应内容
            # 确保请求成功
            if r.status_code == 200:
                bytes_buffer = b''
                for chunk in r.iter_content(chunk_size=1024):
                    bytes_buffer += chunk
                    a = bytes_buffer.find(b'\xff\xd8')  # JPEG 开始
                    b = bytes_buffer.find(b'\xff\xd9')  # JPEG 结束
                    if a != -1 and b != -1:
                        jpg = bytes_buffer[a:b + 2]  # JPEG 图像数据
                        bytes_buffer = bytes_buffer[b + 2:]  # 移除处理过的数据
                        frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                        yield frame

    def video_show(self):
        #image = cv2.imread("D:\SNC_Case\P17.png")
        #image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        #image = image.astype('uint8')
        #qimage = QImage(image.data, self.width, self.height, QImage.Format_RGB888)

        #显示结果
        # pixmap = QPixmap("D:\SNC_Case\P17.png").scaled(self.width, self.height)
        # self.DetectResult.setPixmap(pixmap)
        self.video_status = 0
        self.thread_cam.do_run = True
        stream_url = 'http://localhost:5000/video_feed'
        for frame in self.get_frames(stream_url):
           if self.thread_cam.do_run == False:
              break
           if self.video_status == 0:
              self.cur_frame = frame

           #cv2.imwrite('Cur_frame.png', frame)
           frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
           frame = ImageQt.ImageQt(frame)
           pixmap = QPixmap.fromImage(frame).scaled(self.width, self.height)
           #pixmap = QPixmap("D:\SNC_Case\Cur_frame.png").scaled(self.width, self.height)

           self.VideoStream.setPixmap(pixmap)
           self.VideoStream.setFixedSize(self.width, self.height)
           self.video_status = 1

    def manualDetect(self):
        result = np.random.randint(10, 15, (1,))
        self.DetectResult.setText(str(result))
        # 调用算法，如果出现异常，显示异常物体位置，并触发plc警报，程序在此处挂起（如何操作，不知道）
        res, img = self.anomaly_detection_algrithom()
        if res == 1:
            self.NG_count += 1
            cv2.imwrite(os.path.join('./NG_Result', f'NG_{self.NG_count}.jpg'), img)
        elif res == -1:
            self.DetectResult.setText("请至少选择一种算法")
        # pixmap = QPixmap("D:\SNC_Case\P17.png").scaled(self.width, self.height)
        # self.DetectResult.setPixmap(pixmap)

    def anomaly_detection_algrithom(self):
        #具体算法实现
        #返回res 布尔值 -1未选算法类型 0 正常 1异常;img 定位异常物体的图片

        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        TCV_status = self.TCV.isChecked()
        OD_status = self.OD.isChecked()
        res = 0
        if TCV_status == 1 and OD_status ==1:
            #双流加权检测
            pass
        elif TCV_status == 1 and OD_status == 0:
            #传统算法检测
            pass
        elif TCV_status == 0 and OD_status == 1:
            #Yolo 目标检测
            pass
        else:
            #需要勾选算法模式
            res = -1
        frame = None
        return res, frame

def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()


