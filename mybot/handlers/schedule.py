# Обработчики расписания
from telebot import types
from mybot.handlers.menu import show_main_menu
from mybot.config.schedule_config import EVEN_WEEK_SCHEDULE, ODD_WEEK_SCHEDULE
from datetime import datetime

# Глобальная переменная для хранения текущего типа недели
current_week_is_even = datetime.now().isocalendar()[1] % 2 == 0

def register_handlers(bot):
    @bot.callback_query_handler(func=lambda call: call.data in ['schedule_ir3', 'schedule_common'])
    def schedule_handler(call):
        try:
            if call.data == 'schedule_ir3':
                # Меню расписания для Ир3-23
                markup = types.InlineKeyboardMarkup(row_width=2)
                btn1 = types.InlineKeyboardButton('🔄 Замены', callback_data='schedule_ir3_changes')
                btn2 = types.InlineKeyboardButton('📋 Основное', callback_data='schedule_ir3_main')                
                btn_back = types.InlineKeyboardButton('⬅️ Назад', callback_data='menu')
                markup.add(btn1, btn2)
                markup.add(btn_back)
                text = "📆 Узнать расписание занятий:"
            else:
                # Меню расписания для "Без группы"
                markup = types.InlineKeyboardMarkup(row_width=2)
                btn1 = types.InlineKeyboardButton('🏢 1 корпус', callback_data='schedule_common_1')
                btn2 = types.InlineKeyboardButton('🏢 2 корпус', callback_data='schedule_common_2')
                btn3 = types.InlineKeyboardButton('🏢 3 корпус', callback_data='schedule_common_3')
                btn4 = types.InlineKeyboardButton('🏢 4 корпус', callback_data='schedule_common_4')
                btn5 = types.InlineKeyboardButton('🏢 5 корпус', callback_data='schedule_common_5')
                btn_back = types.InlineKeyboardButton('⬅️ Назад', callback_data='menu')
                markup.row(btn1, btn2)
                markup.row(btn3, btn4)
                markup.row(btn5)
                markup.row(btn_back)
                text = "📅 Выберите корпус:"

            bot.edit_message_text(
                text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
            bot.answer_callback_query(call.id)
        except Exception as e:
            print(f"Ошибка в schedule_handler: {e}")

    @bot.callback_query_handler(func=lambda call: call.data == 'schedule_ir3_changes')
    def show_changes_menu(call):
        try:
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn1 = types.InlineKeyboardButton('🔗 На сегодня', url='https://site/today.htm')
            btn2 = types.InlineKeyboardButton('🔗 На завтра', url='https://site/tomorrow.htm')
            btn_back = types.InlineKeyboardButton('⬅️ Назад', callback_data='schedule_ir3')
            markup.add(btn1, btn2)
            markup.add(btn_back)
            
            bot.edit_message_text(
                "🔄 Выберите день для просмотра замен в расписании:",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
            bot.answer_callback_query(call.id)
        except Exception as e:
            print(f"Ошибка в show_changes_menu: {e}")

    @bot.callback_query_handler(func=lambda call: call.data.startswith('schedule_common_'))
    def show_building_schedule(call):
        try:
            building = call.data.split('_')[-1]
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn1 = types.InlineKeyboardButton('🔗 На сегодня', url=f'https://site/{building}korp/today.htm')
            btn2 = types.InlineKeyboardButton('🔗 На завтра', url=f'https://site/{building}korp/tomorrow.htm')
            btn_back = types.InlineKeyboardButton('⬅️ Назад', callback_data='schedule_common')
            markup.add(btn1, btn2)
            markup.add(btn_back)
            
            bot.edit_message_text(
                f"📅 Расписание {building} корпуса:",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
            bot.answer_callback_query(call.id)
        except Exception as e:
            print(f"Ошибка в show_building_schedule: {e}")

    
    @bot.callback_query_handler(func=lambda call: call.data == 'menu')
    def back_to_menu(call):
        try:
            # Получаем текущий текст и разметку сообщения
            current_text = call.message.text
            current_markup = call.message.reply_markup
            
            # Пытаемся создать новое меню только если оно отличается от текущего
            try:
                show_main_menu(bot, call)
            except Exception as e:
                if "message is not modified" not in str(e):
                    raise e
                else:
                    # Если сообщение не изменилось, просто отвечаем на callback
                    bot.answer_callback_query(call.id)
                
        except Exception as e:
            print(f"Ошибка в back_to_menu: {e}")

    @bot.callback_query_handler(func=lambda call: call.data == 'schedule_ir3_main')
    def show_schedule_days(call):
        try:
            global current_week_is_even
            current_weekday = datetime.now().weekday()
            weekday_mapping = {0: 'mon', 1: 'tue', 2: 'wed', 3: 'thu', 4: 'fri', 5: 'sat'}
            current_day = weekday_mapping.get(current_weekday, 'mon')
            
            schedule = EVEN_WEEK_SCHEDULE if current_week_is_even else ODD_WEEK_SCHEDULE
            
            days_ru = {
                'mon': 'Пн', 'tue': 'Вт', 'wed': 'Ср',
                'thu': 'Чт', 'fri': 'Пт', 'sat': 'Сб'
            }
            
            markup = types.InlineKeyboardMarkup(row_width=6)
            
            # Добавляем все дни недели в одну строку, выделяя текущий
            buttons = []
            for d_code, d_name in days_ru.items():
                if d_code == current_day:
                    btn_text = f"• {d_name} •"
                else:
                    btn_text = d_name
                buttons.append(types.InlineKeyboardButton(
                    btn_text, 
                    callback_data=f'schedule_day_{d_code}'
                ))
            markup.add(*buttons)
            
            # Добавляем кнопки переключения четности недели
            btn_even = types.InlineKeyboardButton(
                f"{'✓ ' if current_week_is_even else ''}Четная неделя", 
                callback_data='schedule_week_even'
            )
            btn_odd = types.InlineKeyboardButton(
                f"{'✓ ' if not current_week_is_even else ''}Нечетная неделя", 
                callback_data='schedule_week_odd'
            )
            markup.row(btn_even, btn_odd)
            
            # Кнопка "Назад"
            btn_back = types.InlineKeyboardButton('⬅️ Назад', callback_data='schedule_ir3')
            markup.row(btn_back)

            # Формируем текст с расписанием
            week_type = "четная" if current_week_is_even else "нечетная"
            text = f"📅 {days_ru[current_day]}, {week_type} неделя:\n\n{schedule[current_day]}"

            bot.edit_message_text(
                text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup,
                parse_mode='HTML'
            )
            bot.answer_callback_query(call.id)
        except Exception as e:
            print(f"Ошибка в show_schedule_days: {e}")

    @bot.callback_query_handler(func=lambda call: call.data.startswith('schedule_week_'))
    def switch_week_schedule(call):
        try:
            global current_week_is_even
            current_week_is_even = call.data.endswith('even')
            schedule = EVEN_WEEK_SCHEDULE if current_week_is_even else ODD_WEEK_SCHEDULE
            
            # Получаем текущий день из сообщения (ищем двухбуквенное сокращение)
            current_text = call.message.text
            day_mapping = {
                'Пн': 'mon', 'Вт': 'tue', 'Ср': 'wed',
                'Чт': 'thu', 'Пт': 'fri', 'Сб': 'sat'
            }
            
            # Ищем день в тексте сообщения
            current_day = 'mon'  # значение по умолчанию
            for ru_day, eng_day in day_mapping.items():
                if ru_day in current_text:
                    current_day = eng_day
                    break
            
            days_ru = {
                'mon': 'Пн', 'tue': 'Вт', 'wed': 'Ср',
                'thu': 'Чт', 'fri': 'Пт', 'sat': 'Сб'
            }
            
            markup = types.InlineKeyboardMarkup(row_width=6)
            
            # Добавляем все дни недели в одну строку, выделяя текущий
            buttons = []
            for d_code, d_name in days_ru.items():
                if d_code == current_day:
                    btn_text = f"• {d_name} •"
                else:
                    btn_text = d_name
                buttons.append(types.InlineKeyboardButton(
                    btn_text, 
                    callback_data=f'schedule_day_{d_code}'
                ))
            markup.add(*buttons)
            
            # Добавляем кнопки переключения четности недели
            btn_even = types.InlineKeyboardButton(
                f"{'✓ ' if current_week_is_even else ''}Четная неделя", 
                callback_data='schedule_week_even'
            )
            btn_odd = types.InlineKeyboardButton(
                f"{'✓ ' if not current_week_is_even else ''}Нечетная неделя", 
                callback_data='schedule_week_odd'
            )
            markup.row(btn_even, btn_odd)
            
            # Кнопка "Назад"
            btn_back = types.InlineKeyboardButton('⬅️ Назад', callback_data='schedule_ir3')
            markup.row(btn_back)

            # Формируем текст с расписанием
            week_type = "четная" if current_week_is_even else "нечетная"
            text = f"📅 {days_ru[current_day]}, {week_type} неделя:\n\n{schedule[current_day]}"

            bot.edit_message_text(
                text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup,
                parse_mode='HTML'
            )
            bot.answer_callback_query(call.id)
            
        except Exception as e:
            print(f"Ошибка в switch_week_schedule: {e}")

    @bot.callback_query_handler(func=lambda call: call.data.startswith('schedule_day_'))
    def show_day_schedule(call):
        try:
            global current_week_is_even
            day = call.data.split('_')[2]
            schedule = EVEN_WEEK_SCHEDULE if current_week_is_even else ODD_WEEK_SCHEDULE
            
            days_ru = {
                'mon': 'Пн', 'tue': 'Вт', 'wed': 'Ср',
                'thu': 'Чт', 'fri': 'Пт', 'sat': 'Сб'
            }

            markup = types.InlineKeyboardMarkup(row_width=6)
            
            # Добавляем все дни недели в одну строку, выделяя текущий
            buttons = []
            for d_code, d_name in days_ru.items():
                if d_code == day:
                    btn_text = f"• {d_name} •"
                else:
                    btn_text = d_name
                buttons.append(types.InlineKeyboardButton(
                    btn_text, 
                    callback_data=f'schedule_day_{d_code}'
                ))
            markup.add(*buttons)

            # Добавляем кнопки переключения четности недели
            btn_even = types.InlineKeyboardButton(
                f"{'✓ ' if current_week_is_even else ''}Четная неделя", 
                callback_data='schedule_week_even'
            )
            btn_odd = types.InlineKeyboardButton(
                f"{'✓ ' if not current_week_is_even else ''}Нечетная неделя", 
                callback_data='schedule_week_odd'
            )
            markup.row(btn_even, btn_odd)

            # Кнопка "Назад"
            btn_back = types.InlineKeyboardButton('⬅️ Назад', callback_data='schedule_ir3')
            markup.row(btn_back)

            week_type = "четная" if current_week_is_even else "нечетная"
            new_text = f"📅 {days_ru[day]}, {week_type} неделя:\n\n{schedule[day]}"

            # Проверяем, изменился ли текст сообщения
            if new_text != call.message.text:
                bot.edit_message_text(
                    new_text,
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=markup,
                    parse_mode='HTML'
                )
            else:
                # Если текст не изменился, обновляем только разметку
                bot.edit_message_reply_markup(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=markup
                )
                
            bot.answer_callback_query(call.id)
        except Exception as e:
            print(f"Ошибка в show_day_schedule: {e}")

    