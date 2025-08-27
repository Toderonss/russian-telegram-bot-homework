from . import base
from . import menu
from . import schedule
from . import homework
from . import admin

def register_all_handlers(bot):
    """Регистрация всех обработчиков"""
    base.register_handlers(bot)
    admin.register_handlers(bot)
    menu.register_handlers(bot)
    schedule.register_handlers(bot)
    homework.register_handlers(bot)
