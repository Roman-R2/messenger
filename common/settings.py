"""
Содержит настройки.
"""

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

# Параметры запросов по умолчанию
GUEST_USER = 'Guest'

# Прококол JIM основные ключи:
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'

# Прочие ключи, используемые в протоколе
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
