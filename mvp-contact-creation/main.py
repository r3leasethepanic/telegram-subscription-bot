import os
import sqlite3
import logging
import asyncio
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

from getcourse_api import gc_import_user, gc_get_contact_uuid, gc_create_order

# ─── Загрузка конфигурации ─────────────────────────────────────────────────
load_dotenv()
TG_TOKEN    = os.getenv("TG_TOKEN")
COURSE_UUID = os.getenv("COURSE_UUID")
RECURRENT   = os.getenv("RECURRENT", "false").lower() == "true"

if not (TG_TOKEN and COURSE_UUID):
    raise RuntimeError("В .env должны быть TG_TOKEN и COURSE_UUID")

# ─── Логирование ───────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s:%(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# ─── Инициализация бота и диспетчера ───────────────────────────────────────
bot = Bot(token=TG_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# ─── Инициализация БД ───────────────────────────────────────────────────────
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    tg_id        INTEGER PRIMARY KEY,
    email        TEXT,
    full_name    TEXT,
    contact_uuid TEXT
)
""")
conn.commit()

# ─── FSM-состояния ─────────────────────────────────────────────────────────
class SubscriptionStates(StatesGroup):
    waiting_for_email = State()
    waiting_for_name  = State()

# ─── On startup: удаляем Webhook и «очищаем» старые updates ────────────────
async def on_startup(dp: Dispatcher):
    # удаляем любые webhook и сбрасываем все накопленные в очереди обновления
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Webhook deleted, pending updates dropped, polling will start")

# ─── Хендлеры ───────────────────────────────────────────────────────────────
@dp.message_handler(commands=["start", "subscribe"])
async def cmd_subscribe(message: types.Message):
    await SubscriptionStates.waiting_for_email.set()
    await message.reply("👋 Введите ваш e-mail для подписки:")

@dp.message_handler(state=SubscriptionStates.waiting_for_email)
async def process_email(message: types.Message, state: FSMContext):
    email = message.text.strip()
    if "@" not in email or "." not in email:
        return await message.reply("❗ Неверный формат e-mail. Попробуйте ещё раз:")
    await state.update_data(email=email)
    await SubscriptionStates.next()
    await message.reply("Теперь укажите ФИО (например: Иван Иванов):")

@dp.message_handler(state=SubscriptionStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    full_name = message.text.strip()
    data = await state.get_data()
    email = data["email"]
    await state.finish()

    try:
        # 1) Импорт/обновление пользователя
        gc_import_user(email, full_name)

        # 2) Получаем UUID контакта
        contact_uuid = gc_get_contact_uuid(email)

        # 3) Сохраняем локально
        cursor.execute(
            "INSERT OR REPLACE INTO users (tg_id,email,full_name,contact_uuid) VALUES (?,?,?,?)",
            (message.from_user.id, email, full_name, contact_uuid)
        )
        conn.commit()

        # 4) Оформляем заказ и получаем ссылку
        payment_link = gc_create_order(contact_uuid, COURSE_UUID, RECURRENT)

        # 5) Отправляем ссылку
        await message.reply(
            "✅ Подписка оформлена!\n"
            f"Перейдите по ссылке для оплаты:\n{payment_link}"
        )
    except Exception as e:
        logger.error(f"Ошибка оформления подписки: {e}")
        await message.reply("❌ Не удалось оформить подписку. Попробуйте позже.")

# ─── Точка входа ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # убеждаемся, что нет других запущенных экземпляров
    for task in asyncio.all_tasks():
        task.cancel()
    # запускаем polling с on_startup
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
