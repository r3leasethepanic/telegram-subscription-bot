import os, sqlite3, logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

from getcourse_api import gc_import_user, gc_get_contact_uuid, gc_create_order

load_dotenv()
TG_TOKEN    = os.getenv("TG_TOKEN")
COURSE_UUID = os.getenv("COURSE_UUID")
RECURRENT   = os.getenv("RECURRENT","false").lower() == "true"

if not (TG_TOKEN and COURSE_UUID):
    raise RuntimeError("TG_TOKEN и COURSE_UUID обязательны в .env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=TG_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Инициализация БД
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
  tg_id      INTEGER PRIMARY KEY,
  email      TEXT,
  full_name  TEXT,
  contact_uuid TEXT
)
""")
conn.commit()

class States(StatesGroup):
    email = State()
    name  = State()

@dp.message_handler(commands=["start","subscribe"])
async def start(message: types.Message):
    await States.email.set()
    await message.reply("Введите e-mail:")

@dp.message_handler(state=States.email)
async def email_handler(message: types.Message, state: FSMContext):
    email = message.text.strip()
    if "@" not in email:
        return await message.reply("Неверный e-mail, попробуйте снова:")
    await state.update_data(email=email)
    await States.next()
    await message.reply("Теперь ФИО:")

@dp.message_handler(state=States.name)
async def name_handler(message: types.Message, state: FSMContext):
    full_name = message.text.strip()
    data = await state.get_data()
    email = data["email"]
    await state.finish()

    try:
        # 1) Импорт/обновление пользователя
        gc_import_user(email, full_name)
        # 2) Поиск его contact_uuid
        uuid = gc_get_contact_uuid(email)
        # 3) Сохранение локально
        cursor.execute(
            "INSERT OR REPLACE INTO users (tg_id,email,full_name,contact_uuid) VALUES(?,?,?,?)",
            (message.from_user.id, email, full_name, uuid)
        )
        conn.commit()
        # 4) Оформление заказа
        link = gc_create_order(uuid, COURSE_UUID, RECURRENT)
        # 5) Ответ пользователю
        await message.reply(f"Регистрация успешна! Оплатить → {link}")
    except Exception as e:
        logger.error(f"Subscription error: {e}")
        await message.reply("Не удалось оформить подписку, попробуйте позже.")
        
async def on_startup(dp):
    # Удаляем все Webhook-методы, чтобы избежать конфликта с Polling
    await bot.delete_webhook()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


