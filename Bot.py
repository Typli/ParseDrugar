from aiogram import Bot
from aiogram.types import User
import logging

# Функция для получения user_id по @username
async def get_user_id_from_username(username: str) -> int:
    try:
        user = await bot.get_chat(username)  # Получаем информацию о пользователе по @username
        return user.id  # Возвращаем user_id
    except Exception as e:
        logging.error(f"Ошибка при получении user_id для {username}: {e}")
        return None

# Функция отправки видео пользователю
async def send_video_to_user(filename, username=None):
    config = load_config()
    if config:
        user_id = None
        if username:
            user_id = await get_user_id_from_username(username)
        else:
            user_id = config.get("user_id")

        if user_id and os.path.exists(filename):
            try:
                async with Bot(token=config["api_token"]) as bot:
                    video_file = FSInputFile(filename)
                    await bot.send_video(user_id, video=video_file, caption="Ваше слайдшоу готово!")
            except Exception as e:
                logging.error(f"Error sending video to user {user_id}: {e}")
