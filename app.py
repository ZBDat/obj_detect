from flask import Flask, Response, request, jsonify, make_response
from yolotest import Detector
import cv2
from cv.edge import edgeDetect
from cv.distortion import trape


app = Flask(__name__)
cap = cv2.VideoCapture(0)
corner_points = {}


# ------------------ - rt video streams for display---------------------
# ----------------------------------------------------------------------
def gen_frames():
    while True:
        ret, frame = cap.read()
        if ret:
            ret, buffer = cv2.imencode('.jpg', frame)
            bframe = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + bframe + b'\r\n\r\n')
        else:
            break

@app.route('/video_feed')  # return rt video stream
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')   
       
# ------------------ get result from yolo detection ---------------------
# -----------------------------------------------------------------------
detector = Detector('best.pt')
    
@app.route('/yolo_result')
def get_yolo_result():
    # ret, frame = cap.read()
    # cv2.imwrite('capture.png', frame)
    ret = True
    frame = './test_images/sample.png'
    if ret:
        bbox_list = detector.detect('capture.png', draw=True) # draw: draw the bounding boxes
        if bbox_list:
            result = 'Object detected!'
        else:
            result = 'safe'
        
        image = cv2.imread('detect.png')
        success, buffer = cv2.imencode('.jpg', image)
        byte_io = buffer.tobytes()
        
        # result is stored in the header
        response = make_response(byte_io)
        response.headers['Content-Type'] = 'image/jpeg'
        response.headers['Result'] = 'Objects detected!'
        
        return response
    
    else:
        return "No frames available!"
    
# ------------------ get results from cv methods -----------------------
# ----------------------------------------------------------------------
@app.route('/corner_points', methods=['PUT'])
def update_corners():
    corner_points = request.json
    return "Corner points updated!"

@app.route('/cv_result')
def get_cv_result():
    if not corner_points:
        return "No transform coordinates available"
    else:
        p1 = corner_points['p1']
        p2 = corner_points['p2']
        p3 = corner_points['p3']
        p4 = corner_points['p4']
        ret, frame = cap.read()
        if ret:
            transformed = trape(frame, p1, p2, p3, p4)
            max_length, max_contour = edgeDetect(transformed)
        else:
            return "No frames available!"

# -------------------------- server tests -------------------------------
# -----------------------------------------------------------------------
@app.route('/')
def index():
    return "Hello!"

@app.route('/img_test')
def get_cur_frame():
    # test if current image is achievable
    ret, frame = cap.read()
    if ret:
        ret, buffer = cv2.imencode('.jpg', frame)
        return Response(buffer.tobytes(), mimetype='image/jpeg') 
    else:
        return "No frame available!"
    
@app.route('/com_test')
def com_test():
    return "Backend is running."


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)  