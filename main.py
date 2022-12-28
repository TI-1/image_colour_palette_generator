import os
import cv2 as cv
import numpy as np

from sklearn.cluster import KMeans
from flask import Flask, render_template, flash, request, url_for, redirect, session
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = "static/Uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app = Flask(__name__)
app.config['SECRET_KEY'] = '' #insert your secret key here
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
Bootstrap(app)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def palette_process():
    img = cv.imread(os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded-file.jpg'))
    dim = (500, 300)
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    img = cv.resize(img, dim, interpolation=cv.INTER_AREA)
    clt = KMeans(n_clusters=10)
    clt.fit(img.reshape(-1, 3))
    hex_codes = []
    pal = np.zeros((10, 3), np.uint8)
    for idx, centers in enumerate(clt.cluster_centers_):
        pal[idx, :] = centers
        h = "#"
        for i in range(3):
            h += "{:02x}".format(pal[idx, i])
        hex_codes.append(h)
    return hex_codes


@app.route('/')
def home():
    session.pop('_flashes', None)
    return render_template("index.html")


@app.route('/', methods=["GET", "POST"])
def upload_file():
    session.pop('_flashes', None)
    if request.method == 'POST':
        # Upload file flask
        if 'uploaded-file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['uploaded-file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded-file.jpg'))
            flash("file uploaded successfully")
            return render_template("index.html")
    return render_template("index.html")


@app.route("/palette")
def palette():
    hex_codes = palette_process()
    return render_template("palette.html", cols=hex_codes)


if __name__ == '__main__':
    app.run(debug=True)
    palette_process()
