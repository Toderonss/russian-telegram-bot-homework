# Работа с хранением JSON данных
import json
import os
from mybot.config.config import DATA_FILE, HOMEWORK_FILE

class Storage:
    @staticmethod
    def ensure_data_dir():
        """Создаем директории и файлы, если они не существуют"""
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        os.makedirs(os.path.dirname(HOMEWORK_FILE), exist_ok=True)
        
        # Создаем пустые файлы с начальной структурой, если их нет
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump({}, f)
        
        if not os.path.exists(HOMEWORK_FILE):
            with open(HOMEWORK_FILE, 'w', encoding='utf-8') as f:
                json.dump({}, f)

    @staticmethod
    def load_data():
        Storage.ensure_data_dir()  # Убедимся, что файлы существуют
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as file:
                return json.load(file)
        except json.JSONDecodeError:
            print("Файл данных поврежден. Создаем новый.")
            empty_data = {}
            Storage.save_data(empty_data)
            return empty_data
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
            return {}

    @staticmethod
    def save_data(data):
        Storage.ensure_data_dir()
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка сохранения данных: {e}")
            return False

    @staticmethod
    def load_homework():
        try:
            if os.path.exists(HOMEWORK_FILE):
                with open(HOMEWORK_FILE, 'r', encoding='utf-8') as file:
                    return json.load(file)
            return {}
        except Exception as e:
            print(f"Error loading homework: {e}")
            return {}

    @staticmethod
    def save_homework(data):
        try:
            with open(HOMEWORK_FILE, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving homework: {e}")
            return False