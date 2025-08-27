from telebot import types

def create_start_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton('👥 Выбрать группу', callback_data='select_group')
    markup.add(btn)
    return markup

def choose_group_selection_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton('👥 Ир3-23', callback_data='group_ir3_23')
    btn2 = types.InlineKeyboardButton('👥 Без группы', callback_data='group_none')
    markup.row(btn1, btn2)
    return markup


def create_switch_group_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton('✅ Да, сменить', callback_data='select_group')
    btn2 = types.InlineKeyboardButton('❌ Нет', callback_data='menu')
    markup.row(btn1, btn2)
    return markup
