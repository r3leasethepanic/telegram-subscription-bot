import os
from aiogram import types
from aiogram.dispatcher import Dispatcher
from bot.getcourse import add_user, create_subscription
from sqlalchemy import insert
from bot.main import SessionLocal, subscriptions

CHANNEL_ID = os.getenv("CHANNEL_ID")

def register_handlers(dp: Dispatcher):
    @dp.message_handler(commands=["start"])
    async def cmd_start(msg: types.Message):
        await msg.reply(
            "👋 Привет!\n"
            "Чтобы оформить подписку, отправьте:\n"
            "/subscribe ваши_email имя"
        )

    @dp.message_handler(commands=["subscribe"])
    async def cmd_subscribe(msg: types.Message):
        args = msg.get_args().split()
        if len(args) < 2:
            return await msg.reply("❗ Формат: /subscribe email имя")
        email, name = args[0], " ".join(args[1:])

        user = add_user(email, name)
        gc_uid = user["id"]

        host = os.getenv("HOST")
        pay_url = create_subscription(gc_uid, f"{host}/webhook/getcourse")

        db = SessionLocal()
        db.execute(insert(subscriptions).values(user_id=gc_uid, tg_id=msg.from_user.id))
        db.commit()

        await msg.reply(f"👉 Оплатите подписку по ссылке:\n{pay_url}")
