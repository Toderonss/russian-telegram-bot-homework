from telebot import types
from datetime import datetime
from mybot.database.storage import Storage
from mybot.keyboards.inline import choose_group_selection_keyboard, create_switch_group_keyboard
from mybot.config.config import ADMIN_IDS

# Дата и время
MONTHS_RU = {
    1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля',
    5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
    9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
}

WEEKDAYS_RU = {
    0: 'понедельник', 1: 'вторник', 2: 'среда',
    3: 'четверг', 4: 'пятница', 5: 'суббота', 6: 'воскресенье'
}


def show_main_menu(bot, call):
    storage = Storage()
    user_data = storage.load_data()
    user_id = str(call.from_user.id)

    # Дата и время
    now = datetime.now()
    current_date = f"{now.day} {MONTHS_RU[now.month]} {now.year}, {WEEKDAYS_RU[now.weekday()]}"
    
    if user_id in user_data and 'group' in user_data[user_id]:
        group = user_data[user_id]['group']
        markup = types.InlineKeyboardMarkup(row_width=2)
        
        if group == 'ir3_23':
            # Меню для группы Ир3-23
            btn1 = types.InlineKeyboardButton('📅 Расписание', callback_data='schedule_ir3')
            btn2 = types.InlineKeyboardButton('📚 Домашнее задание', callback_data='homework_ir3')
            btn3 = types.InlineKeyboardButton('📚 Учебный сайт', url='http://site.ru')
            btn4 = types.InlineKeyboardButton('👥 Сменить группу', callback_data='switchgroup')
            markup.add(btn1, btn2)
            markup.add(btn3, btn4)
            
            # Добавляем кнопку админ-панели только для админа
            if user_id in ADMIN_IDS:
                btn_admin = types.InlineKeyboardButton('👑 Админ панель', callback_data='admin_panel')
                markup.add(btn_admin)
            
            text = (f"👤 Добро пожаловать, {call.from_user.first_name}\n\n"
                    f"Меню группы: Ир3-23\n"
                    f"⏰ {current_date}\n"
                    f"➖➖➖➖➖➖\n"
                    f"📌 Выберите нужный раздел:")
        else:
            # Меню для группы "Без группы"
            text = (f"Меню группы: Без группы\n"
                    f"⏰ {current_date}\n"
                    f"➖➖➖➖➖➖\n"
                    f"❗️ Для доступа ко всем функциям выберите группу")
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            btn1 = types.InlineKeyboardButton('🔄 Замены', callback_data='schedule_common')
            btn2 = types.InlineKeyboardButton('👥 Сменить группу', callback_data='switchgroup')
            markup.row(btn1)
            markup.row(btn2)
            text = (f"Меню группы: (Без группы)\n"
                    f'⏰ {current_date}\n'
                    f'➖➖➖➖➖➖\n'
                    f'❗️ Для доступа ко всем функциям выберите группу')
    else:
        # Если группа не выбрана
        markup = choose_group_selection_keyboard()
        text = "Сначала выберите группу:"
        
    if isinstance(call, types.CallbackQuery):
        # Если это callback query
        bot.edit_message_text(
            text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
        bot.answer_callback_query(call.id)
    else:
        # Если это обычное сообщение или другой тип
        chat_id = call.chat.id if hasattr(call, 'chat') else call.from_user.id
        bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=markup
        )

def register_handlers(bot):
    @bot.callback_query_handler(func=lambda call: call.data == 'main_menu')
    def main_menu_handler(call):
        show_main_menu(bot, call)
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == 'switchgroup')
    def switch_group_handler(call):
        markup = create_switch_group_keyboard()
        bot.edit_message_text(
            'Вы уверены, что хотите сменить группу?',
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data == 'menu')
    def back_to_menu(call):
        show_main_menu(bot, call)
        bot.answer_callback_query(call.id)
