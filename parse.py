import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

# Функция для парсинга данных на указанную дату
def parse_data_for_date(date):
    # Формируем URL с указанной датой
    url = f"https://drugar.su/?date={date}&facility=drugar"

    # Отправляем GET-запрос
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Находим контейнер с фильмами
    event_list = soup.find('div', class_='EventList_event-list-wrap__HHQ1H')

    # Если контейнер не найден, возвращаем пустой список
    if not event_list:
        return []

    # Список для хранения данных о фильмах
    movies_data = []

    # Проходим по каждому фильму
    for event in event_list.find_all('div', class_='EventList_event__OjvqQ'):
        # Извлекаем название фильма
        title = event.find('h2', class_='Title_title__GSkiG').text.strip()

        # Список для хранения сеансов
        shows = []

        # Проходим по каждому сеансу
        for show in event.find_all('div', class_='Show_show__kEocF'):
            time = show.find('div', class_='Show_show-time__iv3r5').text.strip()
            price = show.find('div', class_='Show_price__YStM_').text.strip()

            # Добавляем сеанс в список
            shows.append({
                "time": time,
                "price": price
            })

        # Добавляем фильм и его сеансы в список
        movies_data.append({
            "title": title,
            "shows": shows
        })

    return movies_data

# Получаем текущую дату
today = datetime.now()

# Список для хранения данных за все дни
all_data = {}

# Парсим данные на текущую дату и 2 дня вперед
for i in range(3):  # 0 (сегодня), 1 (завтра), 2 (послезавтра)
    date = (today + timedelta(days=i)).strftime("%Y/%m/%d")
    print(f"Парсинг данных на дату: {date}")
    data = parse_data_for_date(date)
    if data:
        all_data[date] = data

# Сохраняем данные в JSON-файл
filename = f"movies_data_{today.strftime('%Y-%m-%d')}_to_{(today + timedelta(days=2)).strftime('%Y-%m-%d')}.json"
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=4)

print(f"Данные успешно сохранены в файл {filename}")