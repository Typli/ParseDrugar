import subprocess
import os
import json
from datetime import datetime, timedelta


def run_parse_script():
    """Запускает скрипт для парсинга данных (parse.py)."""
    print("Запуск скрипта parse.py для парсинга данных...")
    subprocess.run(['python3', 'parse.py'], check=True)
    print("Парсинг завершен.")


def get_json_filename():
    """Получает имя JSON-файла, созданного parse.py."""
    today_date = datetime.now().strftime("%Y-%m-%d")
    json_filename = f"movies_data_{today_date}_to_{(datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')}.json"
    return json_filename


def run_imagemaker_script(json_filename):
    """Запускает скрипт для создания изображений (imagemaker.py) с использованием созданного JSON-файла."""
    print(f"Запуск скрипта imagemaker.py с файлом {json_filename}...")
    subprocess.run(['python3', 'imagemaker.py'], check=True)
    print("Изображения успешно созданы.")


def get_image_folders(json_filename):
    """Получает список директорий, созданных imagemaker.py."""
    with open(json_filename, 'r', encoding='utf-8') as f:
        all_data = json.load(f)

    # Получаем список директорий, соответствующих датам
    date_dirs = [date.replace("/", "-") for date in all_data.keys()]
    return date_dirs


def run_slideshowmaker_script(date_dirs):
    """Запускает скрипт slideshowmaker.py только для первой папки с изображениями, соответствующей сегодняшней дате."""
    today_date = datetime.now().strftime("%Y-%m-%d")

    # Находим первую папку, которая соответствует сегодняшней дате
    date_dir = next((dir for dir in date_dirs if dir.startswith(today_date)), None)

    if date_dir is None:
        print(f"Ошибка: Не найдено папки для сегодняшней даты ({today_date})!")
        return

    print(f"Запуск скрипта slideshowmaker.py для папки {date_dir}...")

    # Используем относительный путь к скрипту
    script_path = os.path.join(os.getcwd(), "slideshowmaker.py")

    # Путь к папке с изображениями для сегодняшней даты
    date_folder_path = os.path.join(os.getcwd(), date_dir)

    # Проверяем, существует ли папка с изображениями
    if not os.path.isdir(date_folder_path):
        print(f"Ошибка: Папка {date_folder_path} не существует!")
        return  # Прерываем выполнение, если папка не существует

    try:
        # Передаем путь к директории с изображениями для сегодняшней даты
        subprocess.run(['python3', script_path, date_folder_path], check=True)
        print(f"Слайдшоу для папки {date_dir} успешно создано.")
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode() if e.stderr else "Неизвестная ошибка"
        print(f"Ошибка при запуске slideshowmaker.py для {date_dir}: {error_msg}")


def main():
    # Шаг 1: Запуск parse.py для парсинга данных
    run_parse_script()

    # Шаг 2: Получение имени JSON-файла, созданного в parse.py
    json_filename = get_json_filename()

    # Шаг 3: Запуск imagemaker.py с данным JSON-файлом
    run_imagemaker_script(json_filename)

    # Шаг 4: Получение директорий изображений, созданных в imagemaker.py
    date_dirs = get_image_folders(json_filename)

    # Шаг 5: Запуск slideshowmaker.py только для первой папки с сегодняшней датой
    run_slideshowmaker_script(date_dirs)

    print("Процесс завершен!")


if __name__ == "__main__":
    main()