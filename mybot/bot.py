import sys
import os
import time
import signal
import importlib
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telebot import TeleBot
from config.config import BOT_TOKEN
from handlers import base, homework, schedule, menu, admin
from handlers import register_all_handlers

# Создаем экземпляр бота
bot = TeleBot(BOT_TOKEN)

def reload_modules():
    """Перезагрузка всех модулей обработчиков"""
    print("🔄 Перезагрузка модулей...")
    
    # Перезагружаем все основные модули
    modules_to_reload = [
        base, homework, schedule, menu, admin,
        importlib.import_module('mybot.database.storage'),
        importlib.import_module('mybot.keyboards.inline')
    ]
    
    for module in modules_to_reload:
        try:
            importlib.reload(module)
            print(f"✓ Модуль {module.__name__} перезагружен")
        except Exception as e:
            print(f"❌ Ошибка при перезагрузке модуля {module.__name__}: {e}")
    
    print("✅ Все модули перезагружены")

def signal_handler(signum, frame):
    """Обработчик сигнала Ctrl+C"""
    print("\n⌛️ Получен сигнал завершения (Ctrl+C)")
    print("🔄 Перезапуск бота...")
    try:
        bot.stop_polling()
        time.sleep(1)
        restart_bot()
    except Exception as e:
        print(f"❌ Ошибка при остановке бота: {e}")
        sys.exit(1)

def restart_bot():
    """Функция перезапуска бота"""
    try:
        # Перезагружаем все модули для применения изменений
        reload_modules()
        
        # Очищаем все существующие обработчики
        bot.remove_webhook()
        bot.delete_webhook()
        bot.message_handlers.clear()
        bot.callback_query_handlers.clear()
        
        print("🔄 Перезагрузка обработчиков...")
        setup_handlers()
        print("✅ Обработчики перезагружены")
        print("🤖 Запуск бота...")
        main()
    except Exception as e:
        print(f"❌ Ошибка при перезапуске: {e}")
        sys.exit(1)

def setup_handlers():
    """Регистрация обработчиков"""
    print("📝 Регистрация обработчиков...")
    try:
        # Очищаем все существующие обработчики
        bot.remove_webhook()
        bot.delete_webhook()
        bot.message_handlers.clear()
        bot.callback_query_handlers.clear()
        
        # Регистрируем все обработчики через единую функцию
        register_all_handlers(bot)
        print("✅ Все обработчики зарегистрированы")
    except Exception as e:
        print(f"❌ Ошибка при регистрации обработчиков: {e}")
        raise

def main():
    """Запуск бота"""
    # Устанавливаем обработчик сигнала Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    while True:
        try:
            print("🟢 Бот запущен и готов к работе...")
            print("ℹ️  Для перезапуска нажмите Ctrl+C")
            bot.polling(none_stop=True, interval=0)
        except Exception as e:
            print(f"❌ Произошла ошибка: {e}")
            print("🔄 Перезапуск через 3 секунды...")
            time.sleep(3)
            continue

if __name__ == '__main__':
    # Устанавливаем обработчики
    setup_handlers()
    # Запускаем бота
    main()