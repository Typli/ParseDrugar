from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
import subprocess
import os
import threading

app = Flask(__name__)
socketio = SocketIO(app)

# Путь к папке с видео
VIDEO_FOLDER = 'videos'  # В вашем случае, это не используется, так как видео сохраняется в корне


# Функция для запуска start.py и отправки логов через SocketIO
def run_main_script(image_folder):
    # Запуск start.py с аргументом для папки с изображениями
    process = subprocess.Popen(['python3', 'start.py', image_folder], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Чтение логов процесса
    for line in process.stdout:
        socketio.emit('log', {'message': line.strip()})

    process.wait()

    # После завершения процесса ищем файл, который был создан
    # (Предполагается, что видео сохраняется в формате 'YYYY-MM-DD.mp4')
    output_video = None
    for file in os.listdir():
        if file.endswith('.mp4'):  # Ищем видеофайл в текущей директории
            output_video = file
            break

    # Проверяем, существует ли файл
    if output_video:
        socketio.emit('done', {'message': 'Слайдшоу успешно создано!'})
        socketio.emit('enable_download', {'filename': output_video})  # Отправляем правильное имя для скачивания
    else:
        socketio.emit('done', {'message': 'Ошибка при создании слайдшоу!'})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    app.logger.info(f"Скачивание файла: {filename}")
    return send_from_directory(os.getcwd(), filename, as_attachment=True)


# Функция для запуска процесса в отдельном потоке, чтобы не блокировать основной поток Flask
@app.route('/create_slideshow', methods=['POST'])
def create_slideshow():
    # Укажите правильный путь к папке с изображениями
    image_folder = 'images'  # Пример пути к папке с изображениями
    thread = threading.Thread(target=run_main_script, args=(image_folder,))
    thread.start()
    return 'Процесс создания слайдшоу запущен.'


if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
