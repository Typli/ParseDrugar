import os
import json
import logging
import asyncio
import threading
import subprocess
import multiprocessing
from flask import Flask, render_template, send_from_directory, request
from flask_socketio import SocketIO, emit
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.types import FSInputFile

# Flask app setup
app = Flask(__name__)
socketio = SocketIO(app)

# Путь к папке с видео и конфигурации
VIDEO_FOLDER = 'videos'
CONFIG_FILE = 'config.json'

# Инициализация бота
bot = None
dp = None
router = Router()  # Создаем роутер для обработки команд

# Обработчики команд
@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Бот запущен!")

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("Просто отправьте команду /start для старта!")

# Функция для загрузки конфигурации
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return None

# Функция для сохранения конфигурации
def save_config(api_token, user_id):
    config = {"api_token": api_token, "user_id": user_id}
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

# Функция для запуска бота
async def start_bot(api_token, user_id):
    global bot, dp

    bot = Bot(token=api_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)

    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot, skip_updates=True)

# Запуск бота в отдельном процессе
def run_bot_process(api_token, user_id):
    asyncio.run(start_bot(api_token, user_id))

def start_bot_in_background(api_token, user_id):
    bot_process = multiprocessing.Process(target=run_bot_process, args=(api_token, user_id))
    bot_process.daemon = True  # Завершается при завершении основного процесса
    bot_process.start()


# Функция отправки видео пользователю
async def send_video_to_user(filename):
    config = load_config()
    if config:
        user_id = config.get("user_id")
        if user_id and os.path.exists(filename):
            try:
                async with Bot(token=config["api_token"]) as bot:
                    video_file = FSInputFile(filename)  # Используем FSInputFile вместо BufferedReader
                    await bot.send_video(user_id, video=video_file, caption="Ваше слайдшоу готово!")
            except Exception as e:
                logging.error(f"Error sending video to user {user_id}: {e}")


# Функция для запуска main.py и отправки логов через SocketIO
def run_main_script(image_folder):
    process = subprocess.Popen(['python3', 'main.py', image_folder], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    for line in process.stdout:
        socketio.emit('log', {'message': line.strip()})

    process.wait()

    output_video = next((f for f in os.listdir() if f.endswith('.mp4')), None)

    if output_video:
        socketio.emit('done', {'message': 'Слайдшоу успешно создано!'})
        socketio.emit('enable_download', {'filename': output_video})

        # Запускаем асинхронную функцию в отдельном asyncio-цикле
        asyncio.run(send_video_to_user(output_video))
    else:
        socketio.emit('done', {'message': 'Ошибка при создании слайдшоу!'})


# Маршруты Flask
@app.route('/')
def index():
    config = load_config()
    if not config:
        return render_template('config_form.html')
    else:
        start_bot_in_background(config['api_token'], config['user_id'])
        return render_template('index.html')

@app.route('/submit_config', methods=['POST'])
def submit_config():
    api_token = request.form['api_token']
    user_id = request.form['user_id']
    save_config(api_token, user_id)

    start_bot_in_background(api_token, user_id)

    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    app.logger.info(f"Скачивание файла: {filename}")
    return send_from_directory(os.getcwd(), filename, as_attachment=True)

@app.route('/create_slideshow', methods=['POST'])
def create_slideshow():
    image_folder = 'images'
    thread = threading.Thread(target=run_main_script, args=(image_folder,))
    thread.start()
    return 'Процесс создания слайдшоу запущен.'

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
