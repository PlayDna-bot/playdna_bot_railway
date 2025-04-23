from pathlib import Path

# Обновленный скрипт Telegram-бота с проверкой номера телефона, возможностью вернуться назад
# и корректной отменой заявки
main_py_code = """
from aiogram import Bot, Dispatcher, executor, types
import logging
import re
from aiogram.utils.markdown import escape_md

API_TOKEN = "7680517671:AAHRTvxhvuvlEctp8j55KTpxZX_y47SlBGM"
ADMIN_CHAT_ID = 220564316
VIDEO_PLATFORMS = r"(youtu\\.be|youtube\\.com|vk\\.com|disk\\.yandex\\.ru|drive\\.google\\.com)"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()]
)

user_data = {}
steps = ["format", "video", "player_info", "contact"]

def is_valid_video_link(url: str) -> bool:
    return re.search(VIDEO_PLATFORMS, url, re.IGNORECASE) is not None

def is_valid_phone(phone: str) -> bool:
    return re.fullmatch(r"\\+?\\d{10,15}", phone.replace(" ", "")) is not None

@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    user_data[message.from_user.id] = {"step": 0}
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Mini", "Full", "Pro", "Ultra")
    await message.answer("👋 Привет! Это бот PlayDNA.\\nВыбери формат отчёта:", reply_markup=keyboard)

@dp.message_handler(commands=["back"])
async def go_back(message: types.Message):
    uid = message.from_user.id
    if uid in user_data and user_data[uid]["step"] > 0:
        user_data[uid]["step"] -= 1
        await proceed_step(message)

@dp.message_handler()
async def handle_all(message: types.Message):
    uid = message.from_user.id
    if uid not in user_data:
        await message.answer("Нажмите /start, чтобы начать.")
        return

    step = user_data[uid]["step"]
    current = steps[step]

    if message.text.lower() in ["нет", "no", "не надо", "cancel"]:
        await message.answer("❌ Заявка отменена. Нажмите /start для новой заявки.")
        user_data.pop(uid, None)
        return

    if current == "format":
        user_data[uid]["format"] = message.text.strip()
    elif current == "video":
        link = message.text.strip()
        if not is_valid_video_link(link):
            await message.answer("🚫 Некорректная ссылка! Используйте YouTube, VK или Google Диск.")
            return
        user_data[uid]["video"] = link
    elif current == "player_info":
        user_data[uid]["player_info"] = message.text.strip()
    elif current == "contact":
        contact = message.text.strip()
        if not is_valid_phone(contact) and not contact.startswith("@"):
            await message.answer("📵 Укажите корректный номер телефона или @username.")
            return
        user_data[uid]["contact"] = contact

        # Отправка админу
        data = user_data[uid]
        user = message.from_user
        text = (
            "📥 *Новая заявка!*\\n"
            f"🔹 Формат: {escape_md(data['format'])}\\n"
            f"🔗 Видео: {escape_md(data['video'])}\\n"
            f"🎽 Игрок: {escape_md(data['player_info'])}\\n"
            f"📞 Контакт: {escape_md(data['contact'])}\\n\\n"
            f"👤 Отправитель: @{user.username or '—'}\\n"
            f"🆔 ID: `{user.id}`\\n"
            f"🏷 Имя: {escape_md(user.full_name)}"
        )
        await bot.send_message(ADMIN_CHAT_ID, text, parse_mode="Markdown")

        # Завершение
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add("/start")
        await message.answer("✅ Заявка отправлена! Хотите отправить ещё одну?", reply_markup=keyboard)
        user_data.pop(uid, None)
        return

    user_data[uid]["step"] += 1
    await proceed_step(message)

async def proceed_step(message: types.Message):
    uid = message.from_user.id
    step = user_data[uid]["step"]
    prompts = [
        "📎 Пришли ссылку на видео (YouTube, VK, Google Диск):",
        "🎽 Укажи номер игрока, цвет формы и позицию:",
        "📞 Твой контакт для связи:"
    ]
    if step == 1:
        await message.answer(prompts[0], reply_markup=types.ReplyKeyboardRemove())
    elif step == 2:
        await message.answer(prompts[1])
    elif step == 3:
        await message.answer(prompts[2])
"""

output_path = Path("/mnt/data/main.py")
output_path.write_text(main_py_code, encoding="utf-8")
output_path.name

