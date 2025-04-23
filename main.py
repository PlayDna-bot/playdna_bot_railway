from aiogram import Bot, Dispatcher, executor, types
import logging
import re
from aiogram.utils.markdown import escape_md

# Конфигурация
API_TOKEN = "7680517671:AAHRTvxhvuvlEctp8j55KTpxZX_y47SlBGM"
ADMIN_CHAT_ID = 220564316
VIDEO_PLATFORMS = r"(youtu\.be|youtube\.com|vk\.com|disk\.yandex\.ru|drive\.google\.com)"

# Инициализация бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()]
)

user_data = {}

def is_valid_video_link(url: str) -> bool:
    """Проверка валидности ссылки на видео"""
    logging.info(f"Checking video link: {url}")
    return re.search(VIDEO_PLATFORMS, url, re.IGNORECASE) is not None

@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    """Обработчик команды /start"""
    try:
        user_data[message.from_user.id] = {}
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add("Mini", "Full", "Pro", "Ultra")
        
        await message.answer(
            "👋 Привет! Это бот PlayDNA.\nВыбери формат отчёта:",
            reply_markup=keyboard
        )
        logging.info(f"New user: {message.from_user.id}")
    except Exception as e:
        logging.error(f"Error in start_cmd: {str(e)}")

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
    try:
        user_data[message.from_user.id]["format"] = message.text.strip()
        logging.info(f"Format selected: {message.text}")
        await message.answer(
            "📎 Пришли ссылку на видео (YouTube, VK, Google Диск):",
            reply_markup=types.ReplyKeyboardRemove()
        )
    except Exception as e:
        logging.error(f"Error in get_format: {str(e)}")

@dp.message_handler(lambda m: m.from_user.id in user_data and not user_data[m.from_user.id].get("video"))
async def get_video(message: types.Message):
    """Проверка и сохранение ссылки на видео"""
    try:
        video_link = message.text.strip()
        logging.info(f"Received video link: {video_link}")
        
        if not is_valid_video_link(video_link):
            logging.warning(f"Invalid video link: {video_link}")
            await message.answer("🚫 Некорректная ссылка! Используйте YouTube, VK или Google Диск.")
            return
            
        user_data[message.from_user.id]["video"] = video_link
        await message.answer("🎽 Укажи номер игрока, цвет формы и позицию:")
    except Exception as e:
        logging.error(f"Error in get_video: {str(e)}")

@dp.message_handler(lambda m: m.from_user.id in user_data and not user_data[m.from_user.id].get("player_info"))
async def get_player_info(message: types.Message):
    """Сохранение информации об игроке"""
    try:
        user_data[message.from_user.id]["player_info"] = message.text.strip()
        logging.info(f"Player info received: {message.text}")
        await message.answer("📞 Твой контакт для связи:")
    except Exception as e:
        logging.error(f"Error in get_player_info: {str(e)}")

@dp.message_handler(lambda m: m.from_user.id in user_data and not user_data[m.from_user.id].get("contact"))
async def get_contact(message: types.Message):
    """Формирование и отправка заявки"""
    try:
        user = message.from_user
        data = user_data[user.id]
        data["contact"] = message.text.strip()
        logging.info(f"Contact info received: {message.text}")

        # Экранирование пользовательских данных
        format_ = escape_md(data["format"])
        video = escape_md(data["video"])
        player_info = escape_md(data["player_info"])
        contact = escape_md(data["contact"])
        username = escape_md(f"@{user.username}" if user.username else "—")
        user_id = user.id
        name = escape_md(user.full_name)

        admin_msg = (
            "📥 *Новая заявка!*\n"
            f"🔹 Формат: {format_}\n"
            f"🔗 Видео: {video}\n"
            f"🎽 Игрок: {player_info}\n"
            f"📞 Контакт: {contact}\n\n"
            f"👤 Отправитель: {username}\n"
            f"🆔 ID: `{user_id}`\n"
            f"🏷 Имя: {name}"
        )

        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_msg,
            parse_mode="Markdown"
        )
        
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add("/start")
        await message.answer(
            "✅ Готово! Заявка отправлена.\nХотите отправить ещё одну?",
            reply_markup=keyboard
        )

    except Exception as e:
        logging.error(f"Error in get_contact: {str(e)}")
        await message.answer("⚠️ Произошла ошибка. Пожалуйста, попробуйте позже.")
    finally:
        user_data.pop(user.id, None)
        logging.info(f"User data cleared for {user.id}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
