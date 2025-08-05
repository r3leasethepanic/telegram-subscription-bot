import os
import sqlite3
import logging
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

from getcourse_api import gc_import_user

# ========== Настройка ==========
load_dotenv()
API_TOKEN = os.getenv("TG_TOKEN")
if not API_TOKEN:
    raise RuntimeError("TG_TOKEN is not set in .env")

# ========== Логирование ==========
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== Инициализация бота ==========
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# ========== База данных ==========
DB_PATH = "bot.db"
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    tg_id      INTEGER PRIMARY KEY,
    email      TEXT,
    full_name  TEXT,
    gc_user_id TEXT
)
""")
conn.commit()

# ========== FSM-состояния ==========
class SubscriptionStates(StatesGroup):
    waiting_for_email = State()
    waiting_for_name  = State()

# ========== Хендлеры ==========
@dp.message_handler(commands=["start", "subscribe"])
async def cmd_subscribe(message: types.Message):
    await SubscriptionStates.waiting_for_email.set()
    await message.reply("👋 Введите, пожалуйста, ваш E-mail для регистрации:")

@dp.message_handler(state=SubscriptionStates.waiting_for_email)
async def process_email(message: types.Message, state: FSMContext):
    email = message.text.strip()
    if "@" not in email or "." not in email:
        await message.reply("❗ Неправильный формат e-mail. Попробуйте ещё раз:")
        return
    await state.update_data(email=email)
    await SubscriptionStates.next()
    await message.reply("Спасибо! Теперь введите, пожалуйста, ваше ФИО:")

@dp.message_handler(state=SubscriptionStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    full_name = message.text.strip()
    data = await state.get_data()
    email = data["email"]
    await state.finish()

    try:
        user_id = gc_import_user(email, full_name)

        cursor.execute(
            "INSERT OR REPLACE INTO users (tg_id, email, full_name, gc_user_id) VALUES (?, ?, ?, ?)",
            (message.from_user.id, email, full_name, user_id)
        )
        conn.commit()

        await message.reply(f"✅ Пользователь создан в GetCourse. ID: {user_id}")
    except Exception as e:
        logger.error(f"Error importing user to GetCourse: {e}")
        await message.reply("❌ Не удалось создать пользователя. Попробуйте позже.")

# ========== Запуск ==========
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

