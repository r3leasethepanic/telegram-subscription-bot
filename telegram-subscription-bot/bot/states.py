
from aiogram.dispatcher.filters.state import State, StatesGroup

class Form(StatesGroup):
    email = State()
    phone = State()
    city = State()
