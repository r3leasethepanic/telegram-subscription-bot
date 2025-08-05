
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import Dispatcher
from states import Form
from utils import is_valid_email, is_valid_phone

async def start_command(message: types.Message):
    await message.answer("Добро пожаловать! Давайте начнем оформление подписки. Введите ваш email:")
    await Form.email.set()

async def process_email(message: types.Message, state: FSMContext):
    email = message.text
    if not is_valid_email(email):
        await message.answer("Неверный формат email. Попробуйте снова:")
        return
    await state.update_data(email=email)
    await message.answer("Введите ваш номер телефона (только цифры, формат 7XXXXXXXXXX):")
    await Form.phone.set()

async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text
    if not is_valid_phone(phone):
        await message.answer("Неверный формат телефона. Попробуйте снова:")
        return
    await state.update_data(phone=phone)
    await message.answer("Введите ваш город:")
    await Form.city.set()

async def process_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    data = await state.get_data()
    username = message.from_user.username or "Не указан"
    result = (
        f"📝 Ваши данные:

"
        f"📧 Email: {data['email']}
"
        f"📞 Телефон: {data['phone']}
"
        f"🌆 Город: {data['city']}
"
        f"👤 Telegram: @{username}"
    )
    await message.answer(result)
    await state.finish()

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_command, commands=["start", "subscribe"], state="*")
    dp.register_message_handler(process_email, state=Form.email)
    dp.register_message_handler(process_phone, state=Form.phone)
    dp.register_message_handler(process_city, state=Form.city)
