from flask import Flask, render_template, request, send_file, redirect, url_for
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os
import io

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Разрешенные форматы файлов
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    """Проверяет, является ли загружаемый файл изображением."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Отображает главную страницу с формой загрузки."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    """Обрабатывает загрузку изображений, выполняет смешивание и строит гистограммы."""
    if 'image1' not in request.files or 'image2' not in request.files:
        return redirect(url_for('index'))
    
    file1 = request.files['image1']
    file2 = request.files['image2']
    
    if not (allowed_file(file1.filename) and allowed_file(file2.filename)):
        return "Ошибка: загружены неверные файлы"

    img1_path = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
    img2_path = os.path.join(app.config['UPLOAD_FOLDER'], file2.filename)
    
    file1.save(img1_path)
    file2.save(img2_path)

    return process_images(img1_path, img2_path, float(request.form['alpha']))

def process_images(img1_path, img2_path, alpha):
    """Обрабатывает изображения: смешивание и создание гистограмм."""
    img1 = Image.open(img1_path).convert('RGB')
    img2 = Image.open(img2_path).convert('RGB')
    img1, img2 = img1.resize((400, 400)), img2.resize((400, 400))
    blended = Image.blend(img1, img2, alpha)

    result_path = 'static/uploads/result.png'
    hist1_path = 'static/uploads/hist1.png'
    hist2_path = 'static/uploads/hist2.png'
    hist_blended_path = 'static/uploads/hist_blended.png'

    blended.save(result_path)
    plot_histogram(img1, hist1_path)
    plot_histogram(img2, hist2_path)
    plot_histogram(blended, hist_blended_path)

    return render_template("result.html", 
                           result_image=url_for('static', filename='uploads/result.png'), 
                           hist1=url_for('static', filename='uploads/hist1.png'), 
                           hist2=url_for('static', filename='uploads/hist2.png'), 
                           hist_blended=url_for('static', filename='uploads/hist_blended.png'))

def plot_histogram(image, save_path):
    """Создаёт гистограмму цветового распределения изображения."""
    img_array = np.array(image)
    plt.figure()
    plt.hist(img_array.ravel(), bins=256, color='orange', alpha=0.7)
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render передает PORT в переменные окружения
    app.run(host="0.0.0.0", port=port, debug=False)  # Открываем порт для внешнего мира
