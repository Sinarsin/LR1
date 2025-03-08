from flask import Flask, render_template, request
from PIL import Image
import numpy as np
import os

app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
def upload():
    if 'image1' not in request.files or 'image2' not in request.files:
        return "Ошибка: Файлы не загружены", 400
    
    image1 = request.files['image1']
    image2 = request.files['image2']
    alpha = float(request.form['alpha'])

    if image1.filename == "" or image2.filename == "":
        return "Ошибка: Файлы не выбраны", 400

    img1 = Image.open(image1).convert("RGBA")
    img2 = Image.open(image2).convert("RGBA")

    img1 = img1.resize((500, 500))
    img2 = img2.resize((500, 500))

    img1_array = np.array(img1)
    img2_array = np.array(img2)

    blended_array = (alpha * img1_array + (1 - alpha) * img2_array).astype(np.uint8)
    blended_image = Image.fromarray(blended_array)

    output_path = os.path.join(UPLOAD_FOLDER, "result.png")
    blended_image.save(output_path)

    return f'<h1>Результат</h1><img src="/{output_path}" alt="Результат">'

if __name__ == "__main__":
    app.run(debug=True)