# импорт класса Env из библиотеки environs для работы
# с .env файлами (переменными окружения)
from environs import Env
# инициализация объекта класса Env()
env = Env()
# чтение переменных окружения
env.read_env()

# создание класса конфига
class Config:
    def __init__(self):
        # читает секретный ключ для шифрования трафика
        self.secret_key = env('SECRET_KEY')
        # читает строку подключения к БД
        self.database_uri = env('DATABASE_URI')