# Обработчики домашних заданий
from telebot import types
from database.storage import Storage
from utils.states import set_state, get_state
from config.config import USER_STATES, DEFAULT_HOMEWORK_DATA
from handlers.menu import show_main_menu
import importlib

# Словарь для хранения состояний пользователей
user_states = {}

def register_handlers(bot):
    @bot.callback_query_handler(func=lambda call: call.data == 'homework_ir3')
    def homework_handler(call):
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton('📝 Записи', callback_data='notes')
        btn2 = types.InlineKeyboardButton('👁 Посмотреть Д/З', callback_data='view_homework')
        btn3 = types.InlineKeyboardButton('⬅️ Назад', callback_data='menu')
        markup.row(btn1, btn2)
        markup.row(btn3)
        
        bot.edit_message_text(
            "📚 Управление домашними заданиями:",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )

    @bot.callback_query_handler(func=lambda call: call.data == 'view_homework')
    def view_homework(call):
        """Обработчик просмотра стандартных домашних заданий"""
        try:
            # Импортируем актуальные данные из конфига
            from mybot.config import config
            importlib.reload(config)
            
            homework_text = "📚 Текущее домашнее задание:\n\n"
            
            # Используем актуальные данные из конфига
            for subject, hw in config.DEFAULT_HOMEWORK_DATA.items():
                emoji = config.SUBJECT_EMOJI.get(subject, "📘")
                if hw.strip():
                    homework_text += f"{emoji} {subject}:\n└ {hw}\n\n"
                else:
                    homework_text += f"{emoji} {subject}:\n└ Не задано\n\n"
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            btn_back = types.InlineKeyboardButton('⬅️ Назад', callback_data='homework_ir3')
            markup.add(btn_back)
            
            bot.edit_message_text(
                homework_text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
            
        except Exception as e:
            print(f"Ошибка в view_homework: {e}")
            bot.answer_callback_query(call.id, "❌ Произошла ошибка")

    @bot.callback_query_handler(func=lambda call: call.data == 'menu')
    def main_menu_handler(call):
        """Обработчик возврата в главное меню"""
        try:
            from handlers.menu import show_main_menu
            try:
                show_main_menu(bot, call)
            except Exception as e:
                if "message is not modified" not in str(e):
                    raise e
            bot.answer_callback_query(call.id)
        except Exception as e:
            print(f"Ошибка в main_menu_handler: {e}")
            bot.answer_callback_query(call.id, "❌ Произошла ошибка")

    @bot.callback_query_handler(func=lambda call: call.data == 'notes')
    def notes_menu(call):
        """Обработчик для меню управления записями"""
        try:
            # Сбрасываем состояние пользователя при возврате в меню
            if call.from_user.id in user_states:
                del user_states[call.from_user.id]
                
            markup = types.InlineKeyboardMarkup(row_width=2)
            
            # Кнопки управления записями (добавляем префикс note_ для отличия от других callback_data)
            btn_add = types.InlineKeyboardButton('📝 Добавить запись', callback_data='note_add')
            btn_view = types.InlineKeyboardButton('👀 Посмотреть записи', callback_data='note_view')
            btn_edit = types.InlineKeyboardButton('✏️ Изменить запись', callback_data='note_edit')
            btn_delete = types.InlineKeyboardButton('🗑 Удалить запись', callback_data='note_delete')
            btn_back = types.InlineKeyboardButton('⬅️ Назад', callback_data='homework_ir3')
            
            # Добавляем кнопки в клавиатуру
            markup.add(btn_add, btn_view)
            markup.add(btn_edit, btn_delete)
            markup.add(btn_back)

            bot.edit_message_text(
                "📋 Управление записями:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup
            )
            
        except Exception as e:
            print(f"Ошибка в notes_menu: {e}")
            bot.answer_callback_query(call.id, "❌ Произошла ошибка")

    @bot.callback_query_handler(func=lambda call: call.data == 'note_add')
    def add_note(call):
        """Обработчик добавления записи"""
        try:
            # Устанавливаем состояние ожидания ввода предмета
            user_states[call.from_user.id] = 'waiting_subject'
            
            markup = types.InlineKeyboardMarkup()
            btn_cancel = types.InlineKeyboardButton('❌ Отмена', callback_data='notes')
            markup.add(btn_cancel)
            
            bot.edit_message_text(
                f"📝 Введите название записи:\n"
                f'Например: Математика, Физика, История и т.д.',
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup
            )
            bot.register_next_step_handler(call.message, process_subject_step, call.message.message_id)
            
        except Exception as e:
            print(f"Ошибка в add_note: {e}")
            bot.answer_callback_query(call.id, "❌ Произошла ошибка")

    def process_subject_step(message, original_message_id):
        try:
            # Проверяем состояние пользователя
            if message.from_user.id not in user_states or user_states[message.from_user.id] != 'waiting_subject':
                return
                
            subject = message.text
            
            # Удаляем сообщение пользователя с названием предмета
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except:
                pass
            
            # Обновляем состояние
            user_states[message.from_user.id] = 'waiting_homework'
            
            markup = types.InlineKeyboardMarkup()
            btn_cancel = types.InlineKeyboardButton('❌ Отмена', callback_data='notes')
            markup.add(btn_cancel)
            
            try:
                bot.edit_message_text(
                    f"📚 Название записи: {subject}\n\n📝 Введите описание предмета:",
                    chat_id=message.chat.id,
                    message_id=original_message_id,
                    reply_markup=markup
                )
            except Exception as e:
                if "message is not modified" not in str(e):
                    raise e
            
            bot.register_next_step_handler(message, process_homework_step, original_message_id, subject)
            
        except Exception as e:
            print(f"Ошибка в process_subject_step: {e}")
            show_error_message(message.chat.id, original_message_id)

    def process_homework_step(message, original_message_id, subject):
        try:
            # Проверяем состояние пользователя
            if message.from_user.id not in user_states or user_states[message.from_user.id] != 'waiting_homework':
                return
                
            homework_text = message.text
            
            # Удаляем состояние пользователя
            if message.from_user.id in user_states:
                del user_states[message.from_user.id]
            
            # Удаляем сообщение пользователя с текстом домашнего задания
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except:
                pass
            
            # Сохраняем домашнее задание
            storage = Storage()
            user_data = storage.load_data()
            user_id = str(message.from_user.id)
            
            if user_id not in user_data:
                user_data[user_id] = {}
            if 'homework' not in user_data[user_id]:
                user_data[user_id]['homework'] = {}
                
            user_data[user_id]['homework'][subject] = homework_text
            storage.save_data(user_data)
            
            markup = types.InlineKeyboardMarkup()
            btn_back = types.InlineKeyboardButton('⬅️ Назад', callback_data='notes')
            markup.add(btn_back)
            
            bot.edit_message_text(
                f"✅ Запись успешно сохранена!\n\n"
                f"📚 Запись: {subject}\n"
                f"📝 Задание: {homework_text}",
                chat_id=message.chat.id,
                message_id=original_message_id,
                reply_markup=markup
            )
            
        except Exception as e:
            print(f"Ошибка в process_homework_step: {e}")
            show_error_message(message.chat.id, original_message_id)

    @bot.callback_query_handler(func=lambda call: call.data == 'note_view')
    def view_note(call):
        """Обработчик просмотра записей"""
        try:
            storage = Storage()
            user_data = storage.load_data()
            user_id = str(call.from_user.id)
            
            if user_id not in user_data or 'homework' not in user_data[user_id] or not user_data[user_id]['homework']:
                markup = types.InlineKeyboardMarkup()
                btn_back = types.InlineKeyboardButton('⬅️ Назад', callback_data='notes')
                markup.add(btn_back)
                
                bot.edit_message_text(
                    "📝 У вас пока нет сохраненных домашних заданий",
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=markup
                )
                return
            
            homework_text = "📚 Ваши записи:\n\n"
            for subject, hw in user_data[user_id]['homework'].items():
                homework_text += f"📌 {subject}:\n{hw}\n\n"
            
            markup = types.InlineKeyboardMarkup()
            btn_back = types.InlineKeyboardButton('⬅️ Назад', callback_data='notes')
            markup.add(btn_back)
            
            bot.edit_message_text(
                homework_text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
            
        except Exception as e:
            print(f"Ошибка в view_ote: {e}")
            bot.answer_callback_query(call.id, "❌ Произошла ошибка")

    @bot.callback_query_handler(func=lambda call: call.data == 'note_edit')
    def edit_note(call):
        """Обработчик изменения записи"""
        try:
            # Сбрасываем состояние пользователя при входе в меню редактирования
            if call.from_user.id in user_states:
                del user_states[call.from_user.id]
                
            storage = Storage()
            user_data = storage.load_data()
            user_id = str(call.from_user.id)
            
            if user_id not in user_data or 'homework' not in user_data[user_id] or not user_data[user_id]['homework']:
                markup = types.InlineKeyboardMarkup()
                btn_back = types.InlineKeyboardButton('⬅️ Назад', callback_data='notes')
                markup.add(btn_back)
                
                bot.edit_message_text(
                    "📝 У вас нет записей для изменения",
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=markup
                )
                return
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            for subject in user_data[user_id]['homework'].keys():
                btn = types.InlineKeyboardButton(f"📚 {subject}", callback_data=f"note_edit_{subject}")
                markup.add(btn)
            
            btn_back = types.InlineKeyboardButton('⬅️ Назад', callback_data='notes')
            markup.add(btn_back)
            
            bot.edit_message_text(
                "📝 Выберите запись для изменения:",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
            
        except Exception as e:
            print(f"Ошибка в edit_note: {e}")
            bot.answer_callback_query(call.id, "❌ Произошла ошибка")

    @bot.callback_query_handler(func=lambda call: call.data.startswith('note_edit_'))
    def edit_homework(call):
        try:
            if not call.data.startswith('note_edit_option_'):
                subject = call.data.replace('note_edit_', '')
                
                # Получаем текущее описание
                storage = Storage()
                user_data = storage.load_data()
                user_id = str(call.from_user.id)
                current_homework = user_data[user_id]['homework'].get(subject, "Описание отсутствует")
                
                # Создаем клавиатуру с выбором что изменить
                markup = types.InlineKeyboardMarkup(row_width=1)
                btn_name = types.InlineKeyboardButton('📝 Изменить название предмета', 
                                                    callback_data=f'note_edit_option_name_{subject}')
                btn_desc = types.InlineKeyboardButton('✏️ Изменить описание задания', 
                                                    callback_data=f'note_edit_option_desc_{subject}')
                btn_cancel = types.InlineKeyboardButton('❌ Отмена', callback_data='notes')
                
                markup.add(btn_name, btn_desc, btn_cancel)
                
                bot.edit_message_text(
                    f"📚 Запись: {subject}\n"
                    f"📝 Текущее описание:\n{current_homework}\n\n"
                    "Выберите, что хотите изменить:",
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=markup
                )
            
        except Exception as e:
            print(f"Ошибка в edit_homework: {e}")
            bot.answer_callback_query(call.id, "❌ Произошла ошибка")

    @bot.callback_query_handler(func=lambda call: call.data.startswith('note_edit_option_'))
    def process_edit_option(call):
        try:
            # Разбираем callback_data
            _, option, action, subject = call.data.split('_')
            
            markup = types.InlineKeyboardMarkup()
            btn_cancel = types.InlineKeyboardButton('❌ Отмена', callback_data='notes')
            markup.add(btn_cancel)
            
            if action == 'name':
                # Устанавливаем состояние ожидания нового названия
                user_states[call.from_user.id] = 'waiting_new_name'
                message_text = f"📚 Текущий предмет: {subject}\n\n📝 Введите новое название предмета:"
            else:  # action == 'desc'
                # Устанавливаем состояние ожидания нового описания
                user_states[call.from_user.id] = 'waiting_new_desc'
                message_text = f"📚 Предмет: {subject}\n\n📝 Введите новое описание задания:"
            
            bot.edit_message_text(
                message_text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
            
            # Регистрируем следующий шаг в зависимости от выбранного действия
            if action == 'name':
                bot.register_next_step_handler(call.message, process_new_name_step, call.message.message_id, subject)
            else:
                bot.register_next_step_handler(call.message, process_new_desc_step, call.message.message_id, subject)
            
        except Exception as e:
            print(f"Ошибка в process_edit_option: {e}")
            bot.answer_callback_query(call.id, "❌ Произошла ошибка")

    def process_new_name_step(message, original_message_id, old_subject):
        try:
            # Проверяем состояние пользователя
            if message.from_user.id not in user_states or user_states[message.from_user.id] != 'waiting_new_name':
                return
                
            new_subject = message.text
            
            # Удаляем состояние пользователя
            if message.from_user.id in user_states:
                del user_states[message.from_user.id]
            
            # Удаляем сообщение пользователя с новым названием
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except:
                pass
            
            # Обновляем название предмета
            storage = Storage()
            user_data = storage.load_data()
            user_id = str(message.from_user.id)
            
            if old_subject in user_data[user_id]['homework']:
                # Сохраняем старое значение
                homework_text = user_data[user_id]['homework'][old_subject]
                # Удаляем старый ключ
                del user_data[user_id]['homework'][old_subject]
                # Создаем новый ключ с тем же значением
                user_data[user_id]['homework'][new_subject] = homework_text
                storage.save_data(user_data)
                
                markup = types.InlineKeyboardMarkup()
                btn_back = types.InlineKeyboardButton('⬅️ Назад', callback_data='notes')
                markup.add(btn_back)
                
                bot.edit_message_text(
                    f"✅ Название предмета успешно изменено!\n\n"
                    f"📚 Старое название: {old_subject}\n"
                    f"📚 Новое название: {new_subject}",
                    chat_id=message.chat.id,
                    message_id=original_message_id,
                    reply_markup=markup
                )
            
        except Exception as e:
            print(f"Ошибка в process_new_name_step: {e}")
            show_error_message(message.chat.id, original_message_id)

    def process_new_desc_step(message, original_message_id, subject):
        try:
            # Проверяем состояние пользователя
            if message.from_user.id not in user_states or user_states[message.from_user.id] != 'waiting_new_desc':
                return
                
            new_homework = message.text
            
            # Удаляем состояние пользователя
            if message.from_user.id in user_states:
                del user_states[message.from_user.id]
            
            # Удаляем сообщение пользователя с новым описанием
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except:
                pass
            
            # Обновляем домашнее задание
            storage = Storage()
            user_data = storage.load_data()
            user_id = str(message.from_user.id)
            
            user_data[user_id]['homework'][subject] = new_homework
            storage.save_data(user_data)
            
            markup = types.InlineKeyboardMarkup()
            btn_back = types.InlineKeyboardButton('⬅️ Назад', callback_data='notes')
            markup.add(btn_back)
            
            bot.edit_message_text(
                f"✅ Описание задания успешно обновлено!\n\n"
                f"📚 Предмет: {subject}\n"
                f"📝 Новое задание: {new_homework}",
                chat_id=message.chat.id,
                message_id=original_message_id,
                reply_markup=markup
            )
            
        except Exception as e:
            print(f"Ошибка в process_new_desc_step: {e}")
            show_error_message(message.chat.id, original_message_id)

    @bot.callback_query_handler(func=lambda call: call.data == 'note_delete')
    def delete_note(call):
        """Обработчик удаления записи"""
        try:
            storage = Storage()
            user_data = storage.load_data()
            user_id = str(call.from_user.id)
            
            if user_id not in user_data or 'homework' not in user_data[user_id] or not user_data[user_id]['homework']:
                markup = types.InlineKeyboardMarkup()
                btn_back = types.InlineKeyboardButton('⬅️ Назад', callback_data='notes')
                markup.add(btn_back)
                
                bot.edit_message_text(
                    "📝 У вас нет записей для удаления",
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=markup
                )
                return
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            for subject in user_data[user_id]['homework'].keys():
                btn = types.InlineKeyboardButton(f"🗑 {subject}", callback_data=f"note_delete_{subject}")
                markup.add(btn)
            
            btn_back = types.InlineKeyboardButton('⬅️ Назад', callback_data='notes')
            markup.add(btn_back)
            
            bot.edit_message_text(
                "🗑 Выберите запись для удаления:",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
            
        except Exception as e:
            print(f"Ошибка в delete_note: {e}")
            bot.answer_callback_query(call.id, "❌ Произошла ошибка")

    @bot.callback_query_handler(func=lambda call: call.data.startswith('note_delete_'))
    def confirm_delete(call):
        try:
            subject = call.data.replace('note_delete_', '')
            
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn_confirm = types.InlineKeyboardButton('✅ Подтвердить', callback_data=f'note_confirm_delete_{subject}')
            btn_cancel = types.InlineKeyboardButton('❌ Отмена', callback_data='notes')
            markup.add(btn_confirm, btn_cancel)
            
            bot.edit_message_text(
                f"⚠️ Вы уверены, что хотите удалить домашнее задание по предмету '{subject}'?",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
            
        except Exception as e:
            print(f"Ошибка в confirm_delete: {e}")
            bot.answer_callback_query(call.id, "❌ Произошла ошибка")

    @bot.callback_query_handler(func=lambda call: call.data.startswith('note_confirm_delete_'))
    def process_delete(call):
        try:
            subject = call.data.replace('note_confirm_delete_', '')
            
            # Удаляем домашнее задание
            storage = Storage()
            user_data = storage.load_data()
            user_id = str(call.from_user.id)
            
            if subject in user_data[user_id]['homework']:
                del user_data[user_id]['homework'][subject]
                storage.save_data(user_data)
            
            markup = types.InlineKeyboardMarkup()
            btn_back = types.InlineKeyboardButton('⬅️ Назад', callback_data='notes')
            markup.add(btn_back)
            
            bot.edit_message_text(
                f"✅ Домашнее задание по предмету '{subject}' успешно удалено!",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
            
        except Exception as e:
            print(f"Ошибка в process_delete: {e}")
            bot.answer_callback_query(call.id, "❌ Произошла ошибка")

    def show_error_message(chat_id, message_id):
        """Вспомогательная функция для отображения ошибок"""
        try:
            markup = types.InlineKeyboardMarkup()
            btn_back = types.InlineKeyboardButton('⬅️ Назад', callback_data='notes')
            markup.add(btn_back)
            
            bot.edit_message_text(
                "❌ Произошла ошибка. Пожалуйста, попробуйте снова.",
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
        except Exception as e:
            print(f"Ошибка при отображении сообщения об ошибке: {e}")

    # Обработчик для всех callback_query, чтобы сбрасывать состояния при отмене
    @bot.callback_query_handler(func=lambda call: True)
    def handle_all_callbacks(call):
        """Общий обработчик для всех callback запросов"""
        if call.data == 'notes' or call.data == 'homework_ir3':
            # Сбрасываем состояние пользователя при возврате в меню
            if call.from_user.id in user_states:
                del user_states[call.from_user.id]

    @bot.callback_query_handler(func=lambda call: call.data == 'note_view')
    def view_note(call):
        """Обработчик просмотра записей"""
        try:
            storage = Storage()
            user_data = storage.load_data()
            user_id = str(call.from_user.id)
            
            # Проверяем наличие пользовательских записей
            has_user_homework = (user_id in user_data and 
                               'homework' in user_data[user_id] and 
                               user_data[user_id]['homework'])
            
            if not has_user_homework:
                # Если у пользователя нет записей, показываем DEFAULT_HOMEWORK_DATA
                homework_text = "📚 Список стандартных домашних заданий:\n\n"
                for subject, hw in DEFAULT_HOMEWORK_DATA.items():
                    homework_text += f"📌 {subject}:\n{hw}\n\n"
                
                markup = types.InlineKeyboardMarkup(row_width=2)
                btn_add = types.InlineKeyboardButton('📝 Добавить свою запись', callback_data='note_add')
                btn_back = types.InlineKeyboardButton('⬅️ Назад', callback_data='notes')
                markup.add(btn_add)
                markup.add(btn_back)
                
                bot.edit_message_text(
                    homework_text,
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=markup
                )
                return
            
            # Если есть пользовательские записи, показываем их
            homework_text = "📚 Ваши домашние задания:\n\n"
            for subject, hw in user_data[user_id]['homework'].items():
                homework_text += f"📌 {subject}:\n{hw}\n\n"
            
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn_add = types.InlineKeyboardButton('📝 Добавить запись', callback_data='note_add')
            btn_edit = types.InlineKeyboardButton('✏️ Изменить запись', callback_data='note_edit')
            btn_delete = types.InlineKeyboardButton('🗑 Удалить запись', callback_data='note_delete')
            btn_default = types.InlineKeyboardButton('👁 Стандартные Д/З', callback_data='view_default_homework')
            btn_back = types.InlineKeyboardButton('⬅️ Назад', callback_data='notes')
            
            markup.add(btn_add, btn_edit)
            markup.add(btn_delete, btn_default)
            markup.add(btn_back)
            
            bot.edit_message_text(
                homework_text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
            
        except Exception as e:
            print(f"Ошибка в view_note: {e}")
            bot.answer_callback_query(call.id, "❌ Произошла ошибка")
