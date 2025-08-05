import os
import sqlite3
import logging
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

from getcourse_api import gc_import_user, gc_create_order

# ── Настройка ────────────────────────────────────────────────────────────
load_dotenv()
TG_TOKEN    = os.getenv("TG_TOKEN")
COURSE_UUID = os.getenv("COURSE_UUID")       # UUID вашего продукта в GetCourse
RECURRENT   = os.getenv("RECURRENT", "false").lower() == "true"

if not TG_TOKEN or not COURSE_UUID:
    raise RuntimeError("TG_TOKEN и COURSE_UUID должны быть заданы в .env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=TG_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# ── База данных ──────────────────────────────────────────────────────────
conn = sqlite3.connect("bot.db", check_same_thread=False)
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

# ── FSM-состояния ────────────────────────────────────────────────────────
class SubscriptionStates(StatesGroup):
    waiting_for_email = State()
    waiting_for_name  = State()

# ── Хендлеры ────────────────────────────────────────────────────────────
@dp.message_handler(commands=["start", "subscribe"])
async def cmd_subscribe(message: types.Message):
    await SubscriptionStates.waiting_for_email.set()
    await message.reply("👋 Введите ваш e-mail для регистрации:")

@dp.message_handler(state=SubscriptionStates.waiting_for_email)
async def process_email(message: types.Message, state: FSMContext):
    email = message.text.strip()
    if "@" not in email or "." not in email:
        return await message.reply("❗ Неверный формат e-mail. Попробуйте ещё раз:")
    await state.update_data(email=email)
    await SubscriptionStates.next()
    await message.reply("Теперь введите ФИО (например: Иван Иванов):")

@dp.message_handler(state=SubscriptionStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    full_name = message.text.strip()
    data = await state.get_data()
    email = data["email"]
    await state.finish()

    try:
        # 1) Создаём или получаем пользователя в GetCourse
        user_id = gc_import_user(email, full_name)
        # 2) Сохраняем в локальную БД
        cursor.execute(
            "INSERT OR REPLACE INTO users (tg_id, email, full_name, gc_user_id) VALUES (?, ?, ?, ?)",
            (message.from_user.id, email, full_name, user_id)
        )
        conn.commit()
        # 3) Создаём заказ и получаем ссылку на оплату
        payment_link = gc_create_order(user_id, COURSE_UUID, RECURRENT)
        # 4) Отправляем пользователю
        await message.reply(
            "✅ Регистрация прошла успешно!\n"
            f"Перейдите по ссылке для оплаты:\n{payment_link}"
        )
    except Exception as e:
        logger.error(f"Ошибка оформления подписки: {e}")
        await message.reply("❌ Не удалось оформить подписку. Попробуйте позже.")

# ── Запуск ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

