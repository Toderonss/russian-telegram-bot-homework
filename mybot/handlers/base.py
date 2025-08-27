from telebot import types
from mybot.database.storage import Storage
from mybot.keyboards.inline import create_start_keyboard, choose_group_selection_keyboard, create_switch_group_keyboard
from mybot.handlers.menu import show_main_menu

word_id = ['id', 'айди', 'ид', 'шв']

def register_handlers(bot):
    @bot.message_handler(commands=['start'])
    def start(message):
        # Создаем простую клавиатуру с одной кнопкой "Выбрать группу"
        markup = create_start_keyboard()        
        bot.send_message(
            message.chat.id,
            '🤖 Привет! Это Trial version бота для домашних заданий',
            reply_markup=markup
        )

    @bot.callback_query_handler(func=lambda call: call.data == 'select_group')
    def select_group(call):
        # После нажатия на "Выбрать группу" показываем выбор между группами
        markup = choose_group_selection_keyboard()
        bot.edit_message_text(
            "Выберите вашу группу:",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )

    @bot.message_handler(commands=['menu'])
    def menu_command(message):
        show_main_menu(bot, message)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('group_'))
    def group_callback(call):
        try:
            group = call.data.split('_', 1)[1]
            storage = Storage()
            user_data = storage.load_data()
            user_id = str(call.from_user.id)
            
            if user_id not in user_data:
                user_data[user_id] = {}
            user_data[user_id]['group'] = group
            storage.save_data(user_data)
            
            show_main_menu(bot, call)
            
        except Exception as e:
            print(f"Ошибка в group_callback: {e}")
    
    @bot.message_handler(commands=['switchgroup'])
    def switch(message):
        # Создаем простую клавиатуру с одной кнопкой "Выбрать группу"
        markup = create_switch_group_keyboard()        
        bot.send_message(
            message.chat.id,
            'Вы уверены что хотите сменить группу?',
            reply_markup=markup
        )

    @bot.message_handler(func=lambda message: any(word in message.text.lower() for word in word_id))
    def send_user_id(message):
        bot.reply_to(message, f"ID ({message.from_user.first_name}): {message.from_user.id}")