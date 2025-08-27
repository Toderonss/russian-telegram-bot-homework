import os
# Конфигурации, константы, токены
# Токен бота
BOT_TOKEN = 'YOUR_BOT_TOKEN'

# инициализация эмодзи для предметов
SUBJECT_EMOJI = {
    "Математика": "🔠",
    "Экономика": "🧩",
    "Информационные технологии": "👨🏻‍💻",
    "Операционные системы": "💻",
    "Английский": "🎓",
    "История": "📖",
    "Физическая культура": "🏃",
}

# Инициализируем начальные данные
DEFAULT_HOMEWORK_DATA = {
    "Математика": "Выучить определения из лекции",
    "Экономика": "Решить задачи №15, 16",
    "Информационные технологии": "Подготовить презентацию",
    "Операционные системы": "Изучить команды Linux",
    "Английский": "Перевести текст, упр. 5 стр. 27",
    "История": "Написать эссе",
    "Физическая культура": "Сделать 5 отжиманий",
}

# Группы
GROUPS = {
    'group1': 'Ир3-23',
    'groupNone': 'Без группы', #и так далее
    'admin': 'Администратор'
}

# Состояния пользователя
USER_STATES = {
    'waiting_subject': 'waiting_subject',
    'waiting_homework': 'waiting_homework',
    'waiting_edit_homework': 'waiting_edit_homework'
}

# Пути к файлам
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'user_data.json')
HOMEWORK_FILE = os.path.join(BASE_DIR, 'data', 'homework_data.json')

# Админы
ADMIN_IDS = ['0123456789'] #ID пользователей в тг








