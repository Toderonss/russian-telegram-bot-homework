from telebot import types
from mybot.config.config import ADMIN_IDS, USER_STATES, DEFAULT_HOMEWORK_DATA, SUBJECT_EMOJI
from mybot.handlers.menu import show_main_menu
import json
import os
import sys
import importlib

# Словарь для хранения состояний пользователей
user_states = {}

def save_admins(admins):
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.py')
    
    try:
        # Читаем текущий конфиг
        with open(config_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Создаем бэкап на всякий случай
        with open(config_path + '.bak', 'w', encoding='utf-8') as file:
            file.write(content)
        
        # Обновляем только строку с ADMIN_IDS
        lines = content.split('\n')
        admin_list_str = "', '".join(admins)
        new_admin_line = f"ADMIN_IDS = ['{admin_list_str}']"
        
        # Ищем и заменяем строку с ADMIN_IDS
        for i, line in enumerate(lines):
            if line.strip().startswith('ADMIN_IDS'):
                lines[i] = new_admin_line
                break
        
        # Собираем файл обратно
        new_content = '\n'.join(lines)
        
        # Проверяем, что новый контент содержит все необходимые переменные
        if 'BOT_TOKEN' not in new_content:
            print("Ошибка: BOT_TOKEN не найден в конфиге")
            # Восстанавливаем из бэкапа
            with open(config_path + '.bak', 'r', encoding='utf-8') as file:
                content = file.read()
            with open(config_path, 'w', encoding='utf-8') as file:
                file.write(content)
            return False
        
        # Записываем обновленный конфиг
        with open(config_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        # Обновляем глобальную переменную ADMIN_IDS
        global ADMIN_IDS
        ADMIN_IDS = admins
        
        # Перезагружаем конфиг
        try:
            import importlib
            import mybot.config.config as config
            importlib.reload(config)
            
            # Перезагружаем все модули, которые используют ADMIN_IDS
            from mybot.handlers import base, menu
            importlib.reload(base)
            importlib.reload(menu)
            
            # Перезагружаем текущий модуль
            importlib.reload(sys.modules[__name__])
            
        except Exception as e:
            print(f"Ошибка при перезагрузке модулей: {e}")
        
        return True
        
    except Exception as e:
        print(f"Ошибка при сохранении админов: {e}")
        # В случае ошибки восстанавливаем из бэкапа
        try:
            with open(config_path + '.bak', 'r', encoding='utf-8') as file:
                content = file.read()
            with open(config_path, 'w', encoding='utf-8') as file:
                file.write(content)
        except Exception as restore_error:
            print(f"Ошибка при восстановлении из бэкапа: {restore_error}")
        return False

def register_handlers(bot):
    @bot.callback_query_handler(func=lambda call: call.data == 'admin_panel')
    def admin_panel(call):
        try:
            # Проверяем, является ли пользователь администратором
            if str(call.from_user.id) not in ADMIN_IDS:
                print(f"Отказано в доступе. ID {call.from_user.id} не в списке админов")
                bot.answer_callback_query(call.id, "⚠️ У вас нет прав администратора")
                return
            
            # Сбрасываем состояние при входе в админ-панель
            if call.message.chat.id in user_states:
                del user_states[call.message.chat.id]
            
            markup = types.InlineKeyboardMarkup(row_width=2)
            
            # Первый ряд кнопок
            btn_view_hw = types.InlineKeyboardButton('👁 Просмотр Д/З', callback_data='admin_view_hw')
            btn_edit_hw = types.InlineKeyboardButton('✏️ Изменить предметы Д/З', callback_data='admin_edit_hw')
            markup.add(btn_view_hw, btn_edit_hw)
            
            # Второй ряд кнопок
            btn_add_admin = types.InlineKeyboardButton('➕ Добавить админа', callback_data='admin_add')
            btn_admin_list = types.InlineKeyboardButton('👥 Список админов', callback_data='admin_list')
            markup.add(btn_add_admin, btn_admin_list)
            
            # Кнопка "Назад"
            btn_back = types.InlineKeyboardButton('⬅️ Назад', callback_data='main_menu')
            markup.add(btn_back)

            bot.edit_message_text(
                "👑 Панель главного администратора\nВыберите действие:",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
            bot.answer_callback_query(call.id)
            
        except Exception as e:
            print(f"Ошибка в admin_panel: {e}")

    @bot.callback_query_handler(func=lambda call: call.data == 'main_menu')
    def back_to_main_menu(call):
        try:
            # Сбрасываем состояние пользователя при выходе в главное меню
            if call.message.chat.id in user_states:
                del user_states[call.message.chat.id]
            show_main_menu(bot, call)
        except Exception as e:
            print(f"Ошибка при возврате в главное меню: {e}")

    @bot.callback_query_handler(func=lambda call: call.data == 'admin_add')
    def admin_add(call):
        try:
            if str(call.from_user.id) not in ADMIN_IDS:
                bot.answer_callback_query(call.id, "⚠️ У вас нет прав администратора")
                return

            # Устанавливаем состояние ожидания ввода ID
            user_states[call.message.chat.id] = 'waiting_admin_id'

            markup = types.InlineKeyboardMarkup()
            btn_back = types.InlineKeyboardButton('⬅️ Назад', callback_data='admin_panel')
            markup.add(btn_back)

            msg = bot.edit_message_text(
                "👤 Введите ID пользователя, которого хотите сделать администратором:",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
            
            # Рекурсивная функция для повторной регистрации обработчика
            def register_next_handler():
                bot.register_next_step_handler_by_chat_id(
                    call.message.chat.id, 
                    lambda m: process_new_admin_id(m, bot, call.message.message_id, register_next_handler)
                )
            
            # Первая регистрация обработчика
            register_next_handler()
            
        except Exception as e:
            print(f"Ошибка в admin_add: {e}")

    @bot.callback_query_handler(func=lambda call: call.data == 'admin_list')
    def admin_list(call):
        try:
            if str(call.from_user.id) not in ADMIN_IDS:
                bot.answer_callback_query(call.id, "⚠️ У вас нет прав администратора")
                return

            markup = types.InlineKeyboardMarkup()
            
            # Добавляем кнопки удаления для каждого админа
            for admin_id in ADMIN_IDS:
                try:
                    user = bot.get_chat(admin_id)
                    btn_delete = types.InlineKeyboardButton(
                        f"❌ Удалить {user.first_name}", 
                        callback_data=f'admin_delete_{admin_id}'
                    )
                except:
                    # Если не удалось получить информацию о пользователе
                    btn_delete = types.InlineKeyboardButton(
                        f"❌ Удалить ID: {admin_id}", 
                        callback_data=f'admin_delete_{admin_id}'
                    )
                markup.add(btn_delete)
            
            btn_back = types.InlineKeyboardButton('⬅️ Назад', callback_data='admin_panel')
            markup.add(btn_back)

            admin_list_text = "👥 Список администраторов:\n\n"
            for i, admin_id in enumerate(ADMIN_IDS, 1):
                try:
                    user = bot.get_chat(admin_id)
                    admin_list_text += f"{i}. {user.first_name} (ID: {admin_id})\n"
                except:
                    admin_list_text += f"{i}. ID: {admin_id}\n"

            bot.edit_message_text(
                admin_list_text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
            
        except Exception as e:
            print(f"Ошибка в admin_list: {e}")

    @bot.callback_query_handler(func=lambda call: call.data.startswith('admin_delete_'))
    def delete_admin(call):
        try:
            if str(call.from_user.id) not in ADMIN_IDS:
                bot.answer_callback_query(call.id, "⚠️ У вас нет прав администратора")
                return
            
            # Получаем ID админа для удаления
            admin_to_delete = call.data.replace('admin_delete_', '')
            
            # Проверяем, не пытается ли админ удалить сам себя
            if admin_to_delete == str(call.from_user.id):
                bot.answer_callback_query(call.id, "❌ Вы не можете удалить сами себя")
                return
            
            # Удаляем админа
            admins = list(ADMIN_IDS)
            if admin_to_delete in admins:
                admins.remove(admin_to_delete)
                if save_admins(admins):
                    try:
                        # Сначала отправляем уведомление
                        bot.send_message(
                            admin_to_delete,
                            "⚠️ Ваши права администратора были отозваны."
                        )
                        
                        # Затем отправляем новое меню
                        markup_new = types.InlineKeyboardMarkup()
                        btn_menu = types.InlineKeyboardButton('📋 Открыть обновлённое меню', callback_data='main_menu')
                        markup_new.add(btn_menu)
                        bot.send_message(
                            admin_to_delete,
                            "Нажмите кнопку ниже, чтобы открыть обновлённое меню:",
                            reply_markup=markup_new
                        )
                    except Exception as e:
                        print(f"Не удалось отправить сообщение удаленному админу: {e}")
                
                    # Обновляем список админов
                    admin_list(call)
                    bot.answer_callback_query(call.id, "✅ Администратор успешно удален")
                else:
                    bot.answer_callback_query(call.id, "❌ Ошибка при сохранении изменений")
            else:
                bot.answer_callback_query(call.id, "❌ Администратор не найден")
                
        except Exception as e:
            print(f"Ошибка в delete_admin: {e}")
            bot.answer_callback_query(call.id, "❌ Произошла ошибка при удалении администратора")

    @bot.callback_query_handler(func=lambda call: call.data == 'admin_view_hw')
    def admin_view_homework(call):
        try:
            if str(call.from_user.id) not in ADMIN_IDS:
                bot.answer_callback_query(call.id, "⚠️ У вас нет прав администратора")
                return

            # Импортируем актуальные данные из конфига
            from mybot.config import config
            importlib.reload(config)

            homework_text = "📚 Домашние задания:\n\n"
            for subject, hw in config.DEFAULT_HOMEWORK_DATA.items():
                emoji = SUBJECT_EMOJI.get(subject, "📘")
                if hw.strip():
                    homework_text += f"{emoji} {subject}:\n└ {hw}\n\n"
                else:
                    homework_text += f"{emoji} {subject}:\n└ Не задано\n\n"

            markup = types.InlineKeyboardMarkup()
            btn_back = types.InlineKeyboardButton('⬅️ Назад', callback_data='admin_panel')
            markup.add(btn_back)

            try:
                bot.edit_message_text(
                    homework_text,
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=markup
                )
            except Exception as e:
                if "message is not modified" not in str(e):
                    raise e
            bot.answer_callback_query(call.id)

        except Exception as e:
            print(f"Ошибка в admin_view_homework: {e}")

    @bot.callback_query_handler(func=lambda call: call.data == 'admin_edit_hw')
    def admin_edit_homework(call):
        try:
            if str(call.from_user.id) not in ADMIN_IDS:
                bot.answer_callback_query(call.id, "⚠️ У вас нет прав администратора")
                return

            # Импортируем актуальные данные из конфига
            from mybot.config import config
            importlib.reload(config)

            markup = types.InlineKeyboardMarkup(row_width=3)
            
            # Кнопки для каждого предмета
            for i, subject in enumerate(config.DEFAULT_HOMEWORK_DATA.keys()):
                emoji = SUBJECT_EMOJI.get(subject, "📘")
                btn_edit = types.InlineKeyboardButton(f"{emoji} {subject}", callback_data=f'hw_edit_{i}')
                btn_delete = types.InlineKeyboardButton(f"❌", callback_data=f'hw_del_{i}')
                btn_emoji = types.InlineKeyboardButton(f"😀", callback_data=f'hw_emoji_{i}')
                markup.add(btn_edit, btn_emoji, btn_delete)
            
            # Сохраняем соответствие индексов и предметов
            user_states[call.message.chat.id] = {
                'subjects_map': list(config.DEFAULT_HOMEWORK_DATA.keys())
            }
            
            # Кнопка добавления нового предмета
            btn_add = types.InlineKeyboardButton('➕ Добавить предмет', callback_data='add_subj')
            markup.add(btn_add)
            
            # Кнопка "Назад"
            btn_back = types.InlineKeyboardButton('⬅️ Назад', callback_data='admin_panel')
            markup.add(btn_back)

            bot.edit_message_text(
                "✏️ Управление предметами:\n"
                "• Нажмите на предмет для редактирования задания\n"
                "• Нажмите 😀 для изменения эмодзи\n"
                "• Нажмите ❌ для удаления предмета",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
            bot.answer_callback_query(call.id)

        except Exception as e:
            print(f"Ошибка в admin_edit_homework: {e}")

    @bot.callback_query_handler(func=lambda call: call.data.startswith('hw_emoji_'))
    def change_subject_emoji(call):
        try:
            if str(call.from_user.id) not in ADMIN_IDS:
                bot.answer_callback_query(call.id, "⚠️ У вас нет прав администратора")
                return

            # Получаем индекс предмета
            index = int(call.data.replace('hw_emoji_', ''))
            subject = user_states[call.message.chat.id]['subjects_map'][index]
            
            # Устанавливаем состояние ожидания нового эмодзи
            user_states[call.message.chat.id]['state'] = 'waiting_emoji'
            user_states[call.message.chat.id]['subject'] = subject

            markup = types.InlineKeyboardMarkup()
            btn_cancel = types.InlineKeyboardButton('❌ Отмена', callback_data='admin_edit_hw')
            markup.add(btn_cancel)

            current_emoji = SUBJECT_EMOJI.get(subject, "📘")
            bot.edit_message_text(
                f"🔄 Изменение эмодзи для предмета: {subject}\n"
                f"Текущий эмодзи: {current_emoji}\n\n"
                f"Отправьте новый эмодзи:",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
            
            # Регистрируем обработчик для следующего сообщения
            bot.register_next_step_handler(call.message, process_new_emoji, bot, call.message.message_id)
            bot.answer_callback_query(call.id)
            
        except Exception as e:
            print(f"Ошибка в change_subject_emoji: {e}")

    @bot.callback_query_handler(func=lambda call: call.data.startswith('hw_edit_'))
    def edit_subject_homework(call):
        try:
            if str(call.from_user.id) not in ADMIN_IDS:
                bot.answer_callback_query(call.id, "⚠️ У вас нет прав администратора")
                return

            # Получаем индекс предмета
            index = int(call.data.replace('hw_edit_', ''))
            # Получаем название предмета из сохраненного списка
            subject = user_states[call.message.chat.id]['subjects_map'][index]
            
            user_states[call.message.chat.id]['state'] = 'waiting_homework'
            user_states[call.message.chat.id]['subject'] = subject

            markup = types.InlineKeyboardMarkup()
            btn_back = types.InlineKeyboardButton('❌ Отмена', callback_data='admin_edit_hw')
            markup.add(btn_back)

            current_hw = DEFAULT_HOMEWORK_DATA.get(subject, "Не задано")
            emoji = SUBJECT_EMOJI.get(subject, "📘")
            try:
                bot.edit_message_text(
                    f"📝 Редактирование задания по предмету: {emoji} {subject}\n\n"
                    f"Текущее задание:\n{current_hw}\n\n"
                    f"Введите новое задание:",
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=markup
                )
            except Exception as e:
                if "message is not modified" not in str(e):
                    raise e
            
            bot.register_next_step_handler(call.message, process_new_homework, bot, call.message.message_id)
            bot.answer_callback_query(call.id)

        except Exception as e:
            print(f"Ошибка в edit_subject_homework: {e}")

    @bot.callback_query_handler(func=lambda call: call.data.startswith('hw_del_'))
    def delete_subject(call):
        try:
            if str(call.from_user.id) not in ADMIN_IDS:
                bot.answer_callback_query(call.id, "⚠️ У вас нет прав администратора")
                return
            
            # Получаем индекс предмета
            index = int(call.data.replace('hw_del_', ''))
            # Получаем название предмета из сохраненного списка
            subject = user_states[call.message.chat.id]['subjects_map'][index]
            
            # Подтверждение удаления
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn_confirm = types.InlineKeyboardButton('✅ Да', callback_data=f'cdel_{index}')
            btn_cancel = types.InlineKeyboardButton('❌ Нет', callback_data='admin_edit_hw')
            markup.add(btn_confirm, btn_cancel)
            
            emoji = SUBJECT_EMOJI.get(subject, "📘")
            bot.edit_message_text(
                f"❗️ Вы уверены, что хотите удалить предмет {emoji} {subject}?",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
            bot.answer_callback_query(call.id)
            
        except Exception as e:
            print(f"Ошибка в delete_subject: {e}")

    @bot.callback_query_handler(func=lambda call: call.data.startswith('cdel_'))
    def confirm_delete_subject(call):
        try:
            if str(call.from_user.id) not in ADMIN_IDS:
                bot.answer_callback_query(call.id, "⚠️ У вас нет прав администратора")
                return
            
            # Получаем индекс предмета
            index = int(call.data.replace('cdel_', ''))
            # Получаем название предмета из сохраненного списка
            subject = user_states[call.message.chat.id]['subjects_map'][index]
            
            if delete_subject_from_config(subject):
                bot.answer_callback_query(call.id, f"✅ Предмет {subject} удален")
            else:
                bot.answer_callback_query(call.id, "❌ Ошибка при удалении предмета")
            
            # Возвращаемся к списку предметов
            admin_edit_homework(call)
            
        except Exception as e:
            print(f"Ошибка в confirm_delete_subject: {e}")

    @bot.callback_query_handler(func=lambda call: call.data == 'add_subj')
    def add_new_subject(call):
        try:
            if str(call.from_user.id) not in ADMIN_IDS:
                bot.answer_callback_query(call.id, "⚠️ У вас нет прав администратора")
                return
            
            # Устанавливаем состояние ожидания ввода названия предмета
            user_states[call.message.chat.id] = {
                'state': 'waiting_new_subject'
            }
            
            markup = types.InlineKeyboardMarkup()
            btn_cancel = types.InlineKeyboardButton('❌ Отмена', callback_data='admin_edit_hw')
            markup.add(btn_cancel)
            
            bot.edit_message_text(
                "📝 Введите название нового предмета:",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
            
            # Регистрируем обработчик для следующего сообщения
            bot.register_next_step_handler(call.message, process_new_subject, bot, call.message.message_id)
            bot.answer_callback_query(call.id)
            
        except Exception as e:
            print(f"Ошибка в add_new_subject: {e}")

def process_new_subject(message, bot, message_id):
    try:
        if message.chat.id not in user_states or user_states[message.chat.id].get('state') != 'waiting_new_subject':
            return
        
        new_subject = message.text.strip()
        
        # Импортируем актуальные данные из конфига
        from mybot.config import config
        importlib.reload(config)
        
        # Проверяем, не существует ли уже такой предмет
        if new_subject in config.DEFAULT_HOMEWORK_DATA:
            bot.send_message(message.chat.id, "❌ Такой предмет уже существует")
            return
        
        # Добавляем новый предмет с пустым заданием
        if update_homework_data(new_subject, "Не задано"):
            success_text = f"✅ Предмет {new_subject} успешно добавлен!"
            
            # Очищаем состояние
            if message.chat.id in user_states:
                del user_states[message.chat.id]
            
            # Удаляем сообщение с названием предмета
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except Exception as e:
                print(f"Не удалось удалить сообщение: {e}")
            
            # Возвращаемся к списку предметов
            markup = types.InlineKeyboardMarkup()
            btn_back = types.InlineKeyboardButton('⬅️ К списку предметов', callback_data='admin_edit_hw')
            markup.add(btn_back)
            
            try:
                bot.edit_message_text(
                    success_text,
                    chat_id=message.chat.id,
                    message_id=message_id,
                    reply_markup=markup
                )
            except Exception as e:
                print(f"Ошибка при обновлении сообщения: {e}")
                # Если не удалось отредактировать, пробуем отправить новое
                bot.send_message(
                    message.chat.id,
                    success_text,
                    reply_markup=markup
                )
        else:
            bot.send_message(message.chat.id, "❌ Ошибка при добавлении предмета")
        
    except Exception as e:
        print(f"Ошибка в process_new_subject: {str(e)}")
        try:
            bot.send_message(message.chat.id, "❌ Произошла ошибка при добавлении предмета")
        except:
            pass

def process_new_admin_id(message, bot, message_id, register_next):
    try:
        # Проверяем состояние пользователя
        if message.chat.id not in user_states or user_states[message.chat.id] != 'waiting_admin_id':
            return
        
        new_admin_id = message.text.strip()
        
        # Проверяем, является ли введенный текст числом
        if not new_admin_id.isdigit():
            try:
                bot.send_message(message.chat.id, "❌ ID должен состоять только из цифр. Попробуйте снова.")
                # Удаляем сообщение с неверным ID
                bot.delete_message(message.chat.id, message.message_id)
            except Exception as e:
                print(f"Ошибка при отправке сообщения об ошибке: {e}")
            register_next()
            return

        # Проверяем, не является ли уже админом
        if new_admin_id in ADMIN_IDS:
            try:
                bot.send_message(message.chat.id, "❌ Этот пользователь уже является администратором.")
                # Удаляем сообщение с ID существующего админа
                bot.delete_message(message.chat.id, message.message_id)
            except Exception as e:
                print(f"Ошибка при отправке сообщения об ошибке: {e}")
            register_next()
            return

        # Добавляем нового админа
        admins = list(ADMIN_IDS)
        admins.append(new_admin_id)
        if not save_admins(admins):
            try:
                bot.send_message(message.chat.id, "❌ Произошла ошибка при сохранении списка администраторов.")
                # Удаляем сообщение с ID при ошибке
                bot.delete_message(message.chat.id, message.message_id)
            except Exception as e:
                print(f"Ошибка при отправке сообщения об ошибке: {e}")
            return

        # Сбрасываем состояние пользователя
        if message.chat.id in user_states:
            del user_states[message.chat.id]

        success_text = ""
        try:
            user = bot.get_chat(new_admin_id)
            success_text = f"✅ Администратор {user.first_name}\n(ID: {new_admin_id}) успешно добавлен!"
            
            # Отправляем сообщение новому админу
            try:
                # Сначала отправляем уведомление
                bot.send_message(
                    new_admin_id,
                    "🎉 Вам были выданы права администратора!"
                )
                
                # Затем отправляем новое меню
                markup_new = types.InlineKeyboardMarkup()
                btn_menu = types.InlineKeyboardButton('📋 Открыть меню', callback_data='main_menu')
                markup_new.add(btn_menu)
                bot.send_message(
                    new_admin_id,
                    "Нажмите кнопку ниже, чтобы открыть обновлённое меню:",
                    reply_markup=markup_new
                )
            except Exception as e:
                print(f"Не удалось отправить сообщение новому админу: {e}")
                
        except Exception as e:
            print(f"Ошибка при получении информации о пользователе: {e}")
            success_text = f"✅ Администратор (ID: {new_admin_id}) успешно добавлен!"

        try:
            # Обновляем сообщение в чате администратора
            markup = types.InlineKeyboardMarkup()
            btn_back = types.InlineKeyboardButton('⬅️ Назад', callback_data='admin_panel')
            markup.add(btn_back)
            
            bot.edit_message_text(
                success_text,
                chat_id=message.chat.id,
                message_id=message_id,
                reply_markup=markup
            )
            
            # Удаляем сообщение с ID только после успешного добавления
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except Exception as e:
                print(f"Не удалось удалить сообщение с ID: {e}")
                
        except Exception as e:
            if "message is not modified" not in str(e):
                try:
                    bot.send_message(
                        message.chat.id,
                        success_text,
                        reply_markup=markup
                    )
                except Exception as send_error:
                    print(f"Ошибка при отправке сообщения об успехе: {send_error}")

    except Exception as e:
        print(f"Ошибка в process_new_admin_id: {e}")
        try:
            bot.send_message(message.chat.id, "❌ Произошла ошибка при добавлении администратора.")
        except Exception as send_error:
            print(f"Ошибка при отправке сообщения об ошибке: {send_error}")

def process_new_homework(message, bot, message_id):
    """Обрабатывает ввод нового домашнего задания"""
    try:
        # Проверяем состояние пользователя
        if message.chat.id not in user_states or 'state' not in user_states[message.chat.id]:
            return
        
        if user_states[message.chat.id]['state'] != 'waiting_homework':
            return
        
        subject = user_states[message.chat.id]['subject']
        new_homework = message.text.strip()
        
        # Обновляем домашнее задание
        if update_homework_data(subject, new_homework):
            success_text = f"✅ Домашнее задание по предмету {subject} обновлено!"
            
            # Очищаем состояние
            if message.chat.id in user_states:
                del user_states[message.chat.id]
            
            # Удаляем сообщение с текстом задания
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except Exception as e:
                print(f"Не удалось удалить сообщение: {e}")
            
            # Возвращаемся к списку предметов
            markup = types.InlineKeyboardMarkup()
            btn_back = types.InlineKeyboardButton('⬅️ К списку предметов', callback_data='admin_edit_hw')
            markup.add(btn_back)
            
            try:
                bot.edit_message_text(
                    success_text,
                    chat_id=message.chat.id,
                    message_id=message_id,
                    reply_markup=markup
                )
            except Exception as e:
                print(f"Ошибка при обновлении сообщения: {e}")
                # Если не удалось отредактировать, пробуем отправить новое
                bot.send_message(
                    message.chat.id,
                    success_text,
                    reply_markup=markup
                )
        else:
            bot.send_message(message.chat.id, "❌ Ошибка при обновлении задания")
        
    except Exception as e:
        print(f"Ошибка в process_new_homework: {str(e)}")
        try:
            bot.send_message(message.chat.id, "❌ Произошла ошибка при обновлении задания")
        except:
            pass

def update_homework_data(subject, new_homework):
    """Обновляет домашнее задание в config.py и перезагружает все связанные модули"""
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.py')
        
        # Читаем текущий конфиг
        with open(config_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Создаем бэкап
        with open(config_path + '.bak', 'w', encoding='utf-8') as file:
            file.write(content)
        
        # Импортируем актуальные данные из конфига
        from mybot.config import config
        importlib.reload(config)
        
        # Создаем обновленный словарь
        updated_homework = dict(config.DEFAULT_HOMEWORK_DATA)
        updated_homework[subject] = new_homework
        
        # Форматируем новый словарь
        hw_dict_str = "DEFAULT_HOMEWORK_DATA = {\n"
        for subj, hw in updated_homework.items():
            hw_dict_str += f'    "{subj}": "{hw}",\n'
        hw_dict_str += "}"
        
        # Обновляем файл
        lines = content.split('\n')
        in_hw_data = False
        new_lines = []
        
        for line in lines:
            if line.startswith('DEFAULT_HOMEWORK_DATA'):
                new_lines.append(hw_dict_str)
                in_hw_data = True
            elif in_hw_data and line.strip().startswith('}'):
                in_hw_data = False
                continue
            elif not in_hw_data:
                new_lines.append(line)
        
        new_content = '\n'.join(new_lines)
        
        # Сохраняем обновленный конфиг
        with open(config_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        # Перезагружаем все необходимые модули
        try:
            # Перезагружаем конфиг
            importlib.reload(config)
            
            # Обновляем глобальные переменные
            global DEFAULT_HOMEWORK_DATA
            DEFAULT_HOMEWORK_DATA = config.DEFAULT_HOMEWORK_DATA
            
            # Перезагружаем связанные модули
            from mybot.handlers import homework, menu, base
            importlib.reload(homework)
            importlib.reload(menu)
            importlib.reload(base)
            
            # Перезагружаем текущий модуль
            importlib.reload(sys.modules[__name__])
            
        except Exception as e:
            print(f"Ошибка при перезагрузке модулей: {e}")
        
        return True
        
    except Exception as e:
        print(f"Ошибка при обновлении homework_data: {e}")
        # Восстанавливаем из бэкапа при ошибке
        try:
            with open(config_path + '.bak', 'r', encoding='utf-8') as file:
                content = file.read()
            with open(config_path, 'w', encoding='utf-8') as file:
                file.write(content)
        except:
            pass
        return False

def delete_subject_from_config(subject):
    """Удаляет предмет из config.py"""
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.py')
        
        # Читаем текущий конфиг
        with open(config_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Создаем бэкап
        with open(config_path + '.bak', 'w', encoding='utf-8') as file:
            file.write(content)
        
        # Импортируем актуальные данные
        from mybot.config import config
        importlib.reload(config)
        
        # Создаем обновленный словарь без удаляемого предмета
        updated_homework = dict(config.DEFAULT_HOMEWORK_DATA)
        if subject in updated_homework:
            del updated_homework[subject]
        
        # Форматируем новый словарь
        hw_dict_str = "DEFAULT_HOMEWORK_DATA = {\n"
        for subj, hw in updated_homework.items():
            hw_dict_str += f'    "{subj}": "{hw}",\n'
        hw_dict_str += "}"
        
        # Обновляем файл
        lines = content.split('\n')
        in_hw_data = False
        new_lines = []
        
        for line in lines:
            if line.startswith('DEFAULT_HOMEWORK_DATA'):
                new_lines.append(hw_dict_str)
                in_hw_data = True
            elif in_hw_data and line.strip().startswith('}'):
                in_hw_data = False
                continue
            elif not in_hw_data:
                new_lines.append(line)
        
        new_content = '\n'.join(new_lines)
        
        # Сохраняем обновленный конфиг
        with open(config_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        # Перезагружаем модули
        importlib.reload(config)
        from mybot.handlers import homework
        importlib.reload(homework)
        
        return True
        
    except Exception as e:
        print(f"Ошибка при удалении предмета: {e}")
        # Восстанавливаем из бэкапа при ошибке
        try:
            with open(config_path + '.bak', 'r', encoding='utf-8') as file:
                content = file.read()
            with open(config_path, 'w', encoding='utf-8') as file:
                file.write(content)
        except:
            pass
        return False

def process_new_emoji(message, bot, message_id):
    try:
        if message.chat.id not in user_states or 'state' not in user_states[message.chat.id]:
            return
        
        if user_states[message.chat.id]['state'] != 'waiting_emoji':
            return
        
        subject = user_states[message.chat.id]['subject']
        new_emoji = message.text.strip()
        
        # Проверяем, что отправлен эмодзи
        if len(new_emoji) > 2:  # Большинство эмодзи занимают 2 символа в UTF-8
            bot.send_message(message.chat.id, "❌ Пожалуйста, отправьте только один эмодзи")
            return
        
        # Обновляем эмодзи
        if update_subject_emoji(subject, new_emoji):
            success_text = f"✅ Эмодзи для предмета {subject} обновлен на {new_emoji}"
            
            # Очищаем состояние
            if message.chat.id in user_states:
                del user_states[message.chat.id]
            
            # Удаляем сообщение с эмодзи
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except Exception as e:
                print(f"Не удалось удалить сообщение: {e}")
            
            # Возвращаемся к списку предметов
            markup = types.InlineKeyboardMarkup()
            btn_back = types.InlineKeyboardButton('⬅️ К списку предметов', callback_data='admin_edit_hw')
            markup.add(btn_back)
            
            bot.edit_message_text(
                success_text,
                chat_id=message.chat.id,
                message_id=message_id,
                reply_markup=markup
            )
        else:
            bot.send_message(message.chat.id, "❌ Ошибка при обновлении эмодзи")
        
    except Exception as e:
        print(f"Ошибка в process_new_emoji: {str(e)}")
        try:
            bot.send_message(message.chat.id, "❌ Произошла ошибка при обновлении эмодзи")
        except:
            pass

def update_subject_emoji(subject, new_emoji):
    """Обновляет эмодзи предмета в config.py"""
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.py')
        
        # Читаем текущий конфиг
        with open(config_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Создаем бэкап
        with open(config_path + '.bak', 'w', encoding='utf-8') as file:
            file.write(content)
        
        # Импортируем актуальные данные
        from mybot.config import config
        importlib.reload(config)
        
        # Создаем обновленный словарь эмодзи
        updated_emoji = dict(config.SUBJECT_EMOJI)
        updated_emoji[subject] = new_emoji
        
        # Форматируем новый словарь
        emoji_dict_str = "SUBJECT_EMOJI = {\n"
        for subj, emoji in updated_emoji.items():
            emoji_dict_str += f'    "{subj}": "{emoji}",\n'
        emoji_dict_str += "}"
        
        # Обновляем файл
        lines = content.split('\n')
        in_emoji_data = False
        new_lines = []
        
        for line in lines:
            if line.startswith('SUBJECT_EMOJI'):
                new_lines.append(emoji_dict_str)
                in_emoji_data = True
            elif in_emoji_data and line.strip().startswith('}'):
                in_emoji_data = False
                continue
            elif not in_emoji_data:
                new_lines.append(line)
        
        new_content = '\n'.join(new_lines)
        
        # Сохраняем обновленный конфиг
        with open(config_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        # Перезагружаем все необходимые модули
        try:
            # Перезагружаем конфиг
            importlib.reload(config)
            
            # Обновляем глобальные переменные
            global SUBJECT_EMOJI
            SUBJECT_EMOJI = config.SUBJECT_EMOJI
            
            # Перезагружаем связанные модули
            from mybot.handlers import homework, menu, base
            importlib.reload(homework)
            importlib.reload(menu)
            importlib.reload(base)
            
            # Перезагружаем текущий модуль
            importlib.reload(sys.modules[__name__])
            
        except Exception as e:
            print(f"Ошибка при перезагрузке модулей: {e}")
        
        return True
        
    except Exception as e:
        print(f"Ошибка при обновлении эмодзи: {e}")
        # Восстанавливаем из бэкапа при ошибке
        try:
            with open(config_path + '.bak', 'r', encoding='utf-8') as file:
                content = file.read()
            with open(config_path, 'w', encoding='utf-8') as file:
                file.write(content)
        except:
            pass
        return False
