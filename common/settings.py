"""
Содержит общие настройки.
"""
import logging
from pathlib import Path

# Исходная папка проекта
BASE_DIR = Path(__file__).parent.parent

# Порт по умолчанию для сетевого взаимодействия
DEFAULT_PORT = 7777
# IP адрес по умолчанию для подключения клиента
# DEFAULT_IP_ADDRESS = '172.29.160.1'
DEFAULT_IP_ADDRESS = '127.0.0.1'
# DEFAULT_IP_ADDRESS = '192.168.146.230'
# Максимальная очередь подключений
MAX_CONNECTIONS = 5
# Максимальная длинна сообщения в байтах
MAX_PACKAGE_LENGTH = 1024
# Кодировка сообщений
ENCODING = 'utf-8'
# Текущий уровень логирования
LOGGING_LEVEL = logging.DEBUG

# Параметры запросов по умолчанию
GUEST_USER = 'Guest'

# Прококол JIM основные ключи:
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
SENDER = 'sender_nickname'
RECEIVER = 'receiver_nickname'
MESSAGE = 'message'
HTTP_STATUS = 'http_status'
MESSAGE_TEXT = 'message_text'
ERROR_TEXT = 'error_text'

# Ответы к ключам
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
OK = 'ok'
EXIT = 'exit'
