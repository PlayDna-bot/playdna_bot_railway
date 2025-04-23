from pathlib import Path

# Создаем структуру файла main.py с учётом всех правок
main_py_code = '''from aiogram import Bot, Dispatcher, executor, types
import logging
import re

API_TOKEN = "7680517671:AAHRTvxhvuvlEctp8j55KTpxZX_y47SlBGM"
ADMIN_CHAT_ID = 220564316  # ID администратора (gyrenkov)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

user_data = {}

def is_valid_video_link(text):
    return any(x in text.lower() for x in ["youtu", "vk.com", "disk.yandex", "drive.google"])

@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    user_data[message.from_user.id] = {}
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Mini", "Full", "Pro", "Ultra")
    await message.answer("👋 Привет! Это бот PlayDNA.\\nВыбери формат отчёта:", reply_markup=keyboard)
    logging.info(f"Start command received from {message.from_user.id}")

@dp.message_handler(commands=["get_id"])
async def get_id(message: types.Message):
    await message.answer(f"🆔 Ваш ID: `{message.from_user.id}`\\n👤 Username: @{message.from_user.username}", parse_mode="Markdown")

@dp.message_handler(lambda m: m.from_user.id in user_data and not user_data[m.from_user.id].get("format"))
async def get_format(message: types.Message):
    user_data[message.from_user.id]["format"] = message.text.strip()
    await message.answer("📎 Пришли ссылку на видео (YouTube, VK, Google Диск):", reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(lambda m: m.from_user.id in user_data and not user_data[m.from_user.id].get("video"))
async def get_video(message: types.Message):
    video_link = message.text.strip()
    if not is_valid_video_link(video_link):
        await message.answer("🚫 Ссылка некорректна. Пожалуйста, пришли ссылку на YouTube, VK или Google Диск.")
        return
    user_data[message.from_user.id]["video"] = video_link
    await message.answer("🎽 Укажи номер игрока, цвет формы и позицию:")

@dp.message_handler(lambda m: m.from_user.id in user_data and not user_data[m.from_user.id].get("player_info"))
async def get_player_info(message: types.Message):
    user_data[message.from_user.id]["player_info"] = message.text.strip()
    await message.answer("📞 Твой контакт для связи:")

@dp.message_handler(lambda m: m.from_user.id in user_data and not user_data[m.from_user.id].get("contact"))
async def get_contact(message: types.Message):
    contact = message.text.strip()
    user_data[message.from_user.id]["contact"] = contact
    data = user_data[message.from_user.id]
    user = message.from_user

    admin_msg = (
        "📥 Новая заявка!\\n"
        f"🔹 Формат: {data['format']}\\n"
        f"🔗 Видео: {data['video']}\\n"
        f"🎽 Игрок: {data['player_info']}\\n"
        f"📞 Контакт: {data['contact']}\\n\\n"
        f"👤 Отправитель: @{user.username or user.first_name}\\n"
        f"🆔 ID: {user.id}\\n"
        f"🏷 Имя: {user.full_name}"
    )

    try:
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_msg, parse_mode=None)
    except Exception as e:
        logging.error(f"Ошибка при отправке админу: {e}")

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("/start")
    await message.answer("✅ Готово! Ваша заявка отправлена аналитикам.\\nХотите отправить ещё одну?", reply_markup=keyboard)
    user_data.pop(message.from_user.id)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
'''

# Записываем в файл main.py
output_path = Path("/mnt/data/main.py")
output_path.write_text(main_py_code, encoding="utf-8")
output_path

