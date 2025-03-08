from flask import Flask, render_template, request
from PIL import Image
import numpy as np
import os
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Папка для сохранения изображений
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Разрешённые форматы файлов
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    """Проверка, является ли файл изображением"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
def upload():
    # Проверяем, загружены ли файлы
    if 'image1' not in request.files or 'image2' not in request.files:
        return "Ошибка: Файлы не загружены", 400
    
    image1 = request.files['image1']
    image2 = request.files['image2']
    
    if image1.filename == "" or image2.filename == "":
        return "Ошибка: Файлы не выбраны", 400

    # Проверяем расширение файлов
    if not allowed_file(image1.filename) or not allowed_file(image2.filename):
        return "Ошибка: Неподдерживаемый формат файла. Разрешены только PNG, JPG, JPEG.", 400

    alpha = float(request.form['alpha'])

    # Открываем изображения
    img1 = Image.open(image1).convert("RGBA")
    img2 = Image.open(image2).convert("RGBA")

    # Приводим изображения к одинаковому размеру
    img1 = img1.resize((500, 500))
    img2 = img2.resize((500, 500))

    # Преобразуем в массивы numpy
    img1_array = np.array(img1)
    img2_array = np.array(img2)

    # Выполняем смешивание
    blended_array = (alpha * img1_array + (1 - alpha) * img2_array).astype(np.uint8)
    blended_image = Image.fromarray(blended_array)

    # Сохраняем итоговое изображение
    output_path = os.path.join(UPLOAD_FOLDER, "result.png")
    blended_image.save(output_path)

    # Функция для построения гистограммы
    def plot_histogram(image_array):
        fig, ax = plt.subplots()
        colors = ["red", "green", "blue"]
        for i, color in enumerate(colors):
            ax.hist(image_array[:, :, i].flatten(), bins=256, color=color, alpha=0.6)
        ax.set_xlim(0, 255)

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        encoded_image = base64.b64encode(buf.getvalue()).decode("utf-8")
        plt.close(fig)
        return encoded_image

    # Генерируем гистограммы для трёх изображений
    hist_img1 = plot_histogram(img1_array)
    hist_img2 = plot_histogram(img2_array)
    hist_blended = plot_histogram(blended_array)

    return f'''
        <h1>Результат</h1>
        <h2>Смешанное изображение</h2>
        <img src="/{output_path}" alt="Результат"><br><br>

        <h2>Гистограммы</h2>
        <h3>Исходное изображение 1</h3>
        <img src="data:image/png;base64,{hist_img1}" alt="Гистограмма 1"><br>

        <h3>Исходное изображение 2</h3>
        <img src="data:image/png;base64,{hist_img2}" alt="Гистограмма 2"><br>

        <h3>Результат смешивания</h3>
        <img src="data:image/png;base64,{hist_blended}" alt="Гистограмма результата"><br>

        <br><a href="/"><button>Назад</button></a>
    '''

if __name__ == "__main__":
    app.run(debug=True)
