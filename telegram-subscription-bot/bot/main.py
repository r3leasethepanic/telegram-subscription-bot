import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from sqlalchemy import (
    create_engine, MetaData, Table, Column, Integer
)
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./db.sqlite3")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
metadata = MetaData()
subscriptions = Table(
    "subscriptions", metadata,
    Column("user_id", Integer, primary_key=True),
    Column("tg_id",    Integer, nullable=False),
)
metadata.create_all(engine)

TOKEN     = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("HOST") + f"/webhook/telegram/{TOKEN}"
bot       = Bot(token=TOKEN)
dp        = Dispatcher(bot)
app       = FastAPI()

from bot.handlers import register_handlers
register_handlers(dp)

@app.post(f"/webhook/telegram/{{token}}")
async def telegram_webhook(token: str, update: Update):
    if token != TOKEN:
        raise HTTPException(status_code=403)
    await dp.process_update(update)
    return {"ok": True}

@app.post("/webhook/getcourse")
async def getcourse_webhook(request: Request):
    payload = await request.json()
    event   = payload.get("event")
    data    = payload.get("data", {})
    user_id = data.get("user", {}).get("id")
    if not user_id:
        raise HTTPException(400, "No user id")
    db = SessionLocal()
    row = db.execute(subscriptions.select().where(subscriptions.c.user_id == user_id)).first()
    if not row:
        return {"status": "user not found"}
    tg_id = row.tg_id

    if event == "order.paid":
        link = await bot.export_chat_invite_link(os.getenv("CHANNEL_ID"))
        await bot.send_message(tg_id, f"Ваш доступ активирован! Вот ссылка: {link}")
    elif event in ("order.cancelled", "subscription.failed"):
        await bot.kick_chat_member(os.getenv("CHANNEL_ID"), tg_id)
        await bot.send_message(tg_id, "Доступ закрыт — подписка не продлена.")
    return {"status": "ok"}

@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()

if __name__ == "__main__":
    uvicorn.run("bot.main:app", host="0.0.0.0", port=8000)
