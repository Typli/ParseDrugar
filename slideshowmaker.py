import cv2
import os
import re
from PIL import Image

# Получаем имя папки из аргументов
import sys
image_folder = sys.argv[1]  # Папка с изображениями передается как аргумент

output_video = f"{image_folder}.mp4"  # Имя выходного видео
frame_duration = 5  # Длительность каждого кадра в секундах
fps = 30  # Количество кадров в секунду

# Функция для извлечения времени из имени файла (например, "2025-02-16_Название_12-30.jpg" → "12:30")
def extract_time(filename):
    match = re.search(r"(\d{2})-(\d{2})", filename)  # Ищем формат HH-MM
    if match:
        return int(match.group(1)) * 60 + int(match.group(2))  # Преобразуем в минуты (HH*60 + MM)
    return float("inf")  # Если нет времени, ставим "бесконечность", чтобы оно шло в конец

# Получаем список изображений и сортируем их по времени показа
images = [img for img in os.listdir(image_folder) if img.endswith((".jpg", ".png"))]
images = sorted(images, key=extract_time)  # Сортируем по времени

# Проверяем, есть ли изображения
if not images:
    print("Ошибка: В папке нет изображений!")
    exit()

# Определяем размер кадра по первому изображению
first_image = Image.open(os.path.join(image_folder, images[0]))
frame_size = first_image.size  # (ширина, высота)

# Создаем объект VideoWriter
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
video = cv2.VideoWriter(output_video, fourcc, fps, frame_size)

# Обрабатываем изображения и добавляем их в видео
frame_count = fps * frame_duration  # Количество кадров на одно изображение

for img_name in images:
    img_path = os.path.join(image_folder, img_name)
    image = cv2.imread(img_path)

    if image is None:
        print(f"Ошибка: Не удалось загрузить {img_name}")
        continue

    image = cv2.resize(image, frame_size)  # Изменяем размер, если нужно

    for _ in range(frame_count):  # Дублируем кадр на 5 секунд
        video.write(image)

    print(f"Добавлено: {img_name}")

# Завершаем запись видео
video.release()
print(f"Видео сохранено как {output_video}")