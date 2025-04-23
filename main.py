from aiogram import Bot, Dispatcher, executor, types
import logging
import re
from pathlib import Path

# Конфигурация
API_TOKEN = "7680517671:AAHRTvxhvuvlEctp8j55KTpxZX_y47SlBGM"
ADMIN_CHAT_ID = 220564316
VIDEO_PLATFORMS = r"(youtu\.be|youtube\.com|vk\.com|disk\.yandex\.ru|drive\.google\.com)"

# Инициализация бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Временное хранилище данных (рекомендуется заменить на БД)
user_data = {}

def is_valid_video_link(url: str) -> bool:
    """Проверяет валидность ссылки на видео"""
    return re.search(VIDEO_PLATFORMS, url) is not None

@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    """Обработчик команды /start"""
    user_data[message.from_user.id] = {}
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Mini", "Full", "Pro", "Ultra")
    
    await message.answer(
        "👋 Привет! Это бот PlayDNA.\nВыбери формат отчёта:",
        reply_markup=keyboard
    )
    logging.info(f"Новый пользователь: {message.from_user.id}")

@dp.message_handler(commands=["get_id"])
async def get_id(message: types.Message):
    """Показывает ID пользователя"""
    await message.answer(
        f"🆔 Ваш ID: `{message.from_user.id}`\n👤 Username: @{message.from_user.username}",
        parse_mode="Markdown"
    )

@dp.message_handler(lambda m: m.from_user.id in user_data and not user_data[m.from_user.id].get("format"))
async def get_format(message: types.Message):
    """Обработчик выбора формата"""
    user_data[message.from_user.id]["format"] = message.text.strip()
    await message.answer(
        "📎 Пришли ссылку на видео (YouTube, VK, Google Диск):",
        reply_markup=types.ReplyKeyboardRemove()
    )

@dp.message_handler(lambda m: m.from_user.id in user_data and not user_data[m.from_user.id].get("video"))
async def get_video(message: types.Message):
    """Проверка и сохранение ссылки на видео"""
    video_link = message.text.strip()
    
    if not is_valid_video_link(video_link):
        await message.answer("🚫 Некорректная ссылка! Используйте YouTube, VK или Google Диск.")
        return
        
    user_data[message.from_user.id]["video"] = video_link
    await message.answer("🎽 Укажи номер игрока, цвет формы и позицию:")

@dp.message_handler(lambda m: m.from_user.id in user_data and not user_data[m.from_user.id].get("player_info"))
async def get_player_info(message: types.Message):
    """Сохранение информации об игроке"""
    user_data[message.from_user.id]["player_info"] = message.text.strip()
    await message.answer("📞 Твой контакт для связи:")

@dp.message_handler(lambda m: m.from_user.id in user_data and not user_data[m.from_user.id].get("contact"))
async def get_contact(message: types.Message):
    """Формирование и отправка заявки"""
    try:
        user = message.from_user
        data = user_data[user.id]
        data["contact"] = message.text.strip()

        # Формирование сообщения для администратора
        admin_msg = (
            "📥 *Новая заявка!*\n"
            f"🔹 Формат: {data['format']}\n"
            f"🔗 Видео: {data['video']}\n"
            f"🎽 Игрок: {data['player_info']}\n"
            f"📞 Контакт: {data['contact']}\n\n"
            f"👤 Отправитель: @{user.username}\n"
            f"🆔 ID: `{user.id}`\n"
            f"🏷 Имя: {user.full_name}"
        )

        # Отправка администратору
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_msg,
            parse_mode="Markdown"
        )

        # Ответ пользователю
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add("/start")
        
        await message.answer(
            "✅ Готово! Заявка отправлена.\nХотите отправить ещё одну?",
            reply_markup=keyboard
        )

    except Exception as e:
        logging.error(f"Ошибка при обработке заявки: {str(e)}")
        await message.answer("⚠️ Произошла ошибка. Пожалуйста, попробуйте позже.")
    finally:
        user_data.pop(user.id, None)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

