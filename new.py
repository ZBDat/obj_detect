from flask import Flask, Response
import cv2
import numpy as np

app = Flask(__name__)

@app.route('/img_test')
def get_image():
    image = cv2.imread('your test image path')
    _, buffer = cv2.imencode('.jpg', image)
    byte_io = buffer.tobytes()

    return Response(byte_io, mimetype='image/jpeg')

if __name__ == "__main__":
    app.run(debug=True)