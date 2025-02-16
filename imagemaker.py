import json
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
import os

# Путь к JSON-файлу с данными
today_date = datetime.now().strftime("%Y-%m-%d")
json_filename = f"movies_data_{today_date}_to_{(datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')}.json"

# Загрузка данных из JSON-файла
with open(json_filename, 'r', encoding='utf-8') as f:
    all_data = json.load(f)

# Путь к шрифту (относительный путь)
font_path = os.path.join(os.getcwd(), "modern_dot_digital-7.ttf")

# Разрешение изображения
image_width = 2168
image_height = 1084

# Настройки шрифтов
title_font_size = 150  # Размер шрифта для названия
info_font_size = 100  # Размер для времени и стоимости
line_spacing = 5  # Межстрочный интервал для названия

title_font = ImageFont.truetype(font_path, title_font_size)
info_font = ImageFont.truetype(font_path, info_font_size)

# Отступы
top_margin = 310  # Отступ сверху для названия
bottom_margin = 310  # Отступ снизу для времени и стоимости
middle_spacing = 300  # Расстояние между названием и временем/стоимостью
max_text_width = image_width * 2 // 3  # Ограничение по ширине (2/3 экрана)


# Функция для переноса текста
def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + " " + word if current_line else word
        bbox = font.getbbox(test_line)
        text_width = bbox[2] - bbox[0]

        if text_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


# Функция для создания изображения
def create_image(title, time, price, output_filename):
    image = Image.new('RGB', (image_width, image_height), color='black')
    draw = ImageDraw.Draw(image)

    # Перенос названия, если оно длинное
    title_lines = wrap_text(title, title_font, max_text_width)

    # Вычисляем высоту текста с учетом межстрочного интервала
    title_height = sum(title_font.getbbox(line)[3] - title_font.getbbox(line)[1] for line in title_lines)
    title_height += line_spacing * (len(title_lines) - 1)

    # Координаты для названия (центрировано по горизонтали, отступ сверху)
    y_offset = top_margin
    for line in title_lines:
        bbox = title_font.getbbox(line)
        text_width = bbox[2] - bbox[0]
        x = (image_width - text_width) // 2
        draw.text((x, y_offset), line, font=title_font, fill='white')
        y_offset += bbox[3] - bbox[1] + line_spacing  # Сдвиг вниз с учетом межстрочного интервала

    # Формируем строку для времени и стоимости
    info_text = f"{time} {price.rstrip()}"
    bbox = info_font.getbbox(info_text)
    info_width = bbox[2] - bbox[0]
    info_height = bbox[3] - bbox[1]

    # Координаты для времени и стоимости (центрировано по горизонтали, отступ снизу)
    x_info = (image_width - info_width) // 2
    y_info = image_height - bottom_margin - info_height
    draw.text((x_info, y_info), info_text, font=info_font, fill='white')

    # Сохраняем изображение
    image.save(output_filename)


# Проходим по каждой дате в данных
for date, movies_data in all_data.items():
    # Создаем директорию для даты
    date_dir = date.replace("/", "-")  # Заменяем "/" на "-" для корректного имени папки
    os.makedirs(date_dir, exist_ok=True)

    # Проходим по каждому фильму и его сеансам
    for movie in movies_data:
        title = movie['title']
        for show in movie['shows']:
            time = show['time']
            price = show['price']

            # Очищаем цену: удаляем тонкий пробел и заменяем "₽" на "р"
            price_cleaned = price.replace('\u2009', '').replace('₽', 'р')

            # Формируем путь к файлу в директории
            output_filename = os.path.join(date_dir, f"{title}_{time.replace(':', '-')}.jpg")

            # Создаем изображение
            create_image(title, time, price_cleaned, output_filename)
            print(f"Создано изображение: {output_filename}")