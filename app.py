import cv2
from flask import Flask, render_template, url_for, request, flash, redirect, jsonify
import numpy as np
from PIL import Image
from table_detection import compute_coordinates

app = Flask(__name__)
app.secret_key = "super secret key"

@app.route('/', methods = ['GET'])
def index():
    return "Please go to this url: http://127.0.0.1:5000/detect/table/"

@app.route('/detect/table/', methods = ['POST', 'GET'])
def table_detect():
    if request.method == 'POST':
        image = request.files['image']
        if not image:
            flash('No selected file')
            return render_template('index.html')
        image_name = image.filename
        flash('Select another file')
        img = Image.open(image.stream)
        pimg = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        x1, y1, x2, y2 = compute_coordinates(pimg)
        print("x1, y1, x2, y2 :", x1, y1, x2, y2)
        return jsonify({image_name: [x1, y1, x2, y2]})        
    
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(debug = True)