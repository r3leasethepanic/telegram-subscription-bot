import sqlite3
import os
from dotenv import load_dotenv

# Загружаем .env, чтобы получить DB_PATH
load_dotenv()
DB_PATH = os.getenv('DB_PATH', 'users.db')

def init_db():
    """Создаёт таблицу users, если её ещё нет"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            telegram_id INTEGER NOT NULL
        )
        '''
    )
    conn.commit()
    conn.close()

def save_user(email: str, telegram_id: int):
    """Сохраняет или обновляет связь email → telegram_id"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        'INSERT OR REPLACE INTO users (email, telegram_id) VALUES (?, ?)',
        (email, telegram_id)
    )
    conn.commit()
    conn.close()

def get_telegram_id(email: str) -> int:
    """Возвращает telegram_id по email или None, если нет"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT telegram_id FROM users WHERE email = ?', (email,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

