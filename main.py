
from aiogram import Bot, Dispatcher, executor, types
import logging

API_TOKEN = "7680517671:AAHRTvxhvuvlEctp8j55KTpxZX_y47SlBGM"
ADMIN_CHAT_ID = 220564316

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
user_data = {}

@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    user_data[message.from_user.id] = {}
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Mini", "Full", "Pro", "Ultra")
    await message.answer("👋 Привет! Это бот PlayDNA.\nВыбери формат отчёта:", reply_markup=keyboard)
    logging.info(f"Start command received from {message.from_user.id}")

@dp.message_handler(commands=["get_id"])
async def get_id(message: types.Message):
    await message.answer(f"🆔 Ваш ID: `{message.from_user.id}`\n👤 Username: @{message.from_user.username}", parse_mode="Markdown")

@dp.message_handler(lambda m: m.from_user.id in user_data and not user_data[m.from_user.id].get("format"))
async def get_format(message: types.Message):
    user_data[message.from_user.id]["format"] = message.text
    await message.answer("📎 Пришли ссылку на видео (YouTube, VK, Google Диск):", reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(lambda m: m.from_user.id in user_data and not user_data[m.from_user.id].get("video"))
async def get_video(message: types.Message):
    user_data[message.from_user.id]["video"] = message.text
    await message.answer("🎽 Укажи номер игрока, цвет формы и позицию:")

@dp.message_handler(lambda m: m.from_user.id in user_data and not user_data[m.from_user.id].get("player_info"))
async def get_player_info(message: types.Message):
    user_data[message.from_user.id]["player_info"] = message.text
    await message.answer("📞 Твой контакт для связи:")

@dp.message_handler(lambda m: m.from_user.id in user_data and not user_data[m.from_user.id].get("contact"))
async def get_contact(message: types.Message):
    user_data[message.from_user.id]["contact"] = message.text
    user = message.from_user
    data = user_data[user.id]
    admin_msg = (
        "📥 *Новая заявка!*
"
        f"🔹 Формат: {data['format']}
"
        f"🔗 Видео: {data['video']}
"
        f"🎽 Игрок: {data['player_info']}
"
        f"📞 Контакт: {data['contact']}

"
        f"👤 Отправитель: @{user.username}
"
        f"🆔 ID: `{user.id}`
"
        f"🏷 Имя: {user.full_name}"
    )
    await bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_msg, parse_mode="Markdown")
    await message.answer("✅ Готово! Ваша заявка отправлена аналитикам.", reply_markup=types.ReplyKeyboardRemove())
    logging.info(f"Заявка от {user.id} отправлена администратору")
    user_data.pop(user.id)

if __name__ == "__main__":
    logging.info("Бот запущен...")
    executor.start_polling(dp, skip_updates=True)
