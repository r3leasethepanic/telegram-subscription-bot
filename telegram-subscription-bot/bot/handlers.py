from aiogram import F
from aiogram.types import Message
from aiogram import Dispatcher
from bot.getcourse import add_user

def register_handlers(dp: Dispatcher):
    @dp.message(F.text == "/start")
    async def start_handler(message: Message):
        tg_username = message.from_user.username
        await message.answer("👋 Привет! Напиши свой Email:")
        dp.message.middleware.register(CollectDataMiddleware(tg_username))

class CollectDataMiddleware:
    def __init__(self, tg_username):
        self.tg_username = tg_username
        self.state = {}

    async def __call__(self, handler, event, data):
        user_id = event.from_user.id
        text = event.text
        if user_id not in self.state:
            self.state[user_id] = {"step": 1, "username": self.tg_username}

        step = self.state[user_id]["step"]
        if step == 1:
            self.state[user_id]["email"] = text
            self.state[user_id]["step"] = 2
            await event.answer("📱 Введите телефон (только цифры, без +):")
            return
        elif step == 2:
            phone = text.strip()
            if not phone.isdigit():
                await event.answer("❌ Телефон должен содержать только цифры. Попробуйте снова:")
                return
            self.state[user_id]["phone"] = phone
            self.state[user_id]["step"] = 3
            await event.answer("🏙️ Введите ваш город:")
            return
        elif step == 3:
            self.state[user_id]["city"] = text
            self.state[user_id]["step"] = 4
            await event.answer("✅ Спасибо! Отправляем данные...")
            await add_user(self.state[user_id])
            await event.answer("🟢 Готово. Вас добавят в канал после оплаты.")
            del self.state[user_id]
            return
        await handler(event, data)
