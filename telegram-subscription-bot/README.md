# Telegram Subscription Bot (MVP)

Простой бот на aiogram для сбора данных пользователя:
- Email
- Телефон (в формате 7XXXXXXXXXX)
- Город
- Telegram username (автоматически)

## Установка

1. Клонируй репозиторий или распакуй zip.
2. Установи зависимости:

```
pip install -r requirements.txt
```

3. Создай `.env` файл и добавь свой токен:

```
BOT_TOKEN=твой_токен_бота
```

4. Запусти бота:

```
python bot/main.py
```