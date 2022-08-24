"""
Содержит сервисные классы и функции
"""
import inspect
import logging
import time

from common import settings
from common.services import HTTPStatus

from app_client_side import logging_config

# Инициализация логирования сервера.
CLIENT_LOGGER = logging.getLogger('client_logger')


def debug_logger(func):
    def deco(*args, **kwargs):
        result = func(*args, **kwargs)
        CLIENT_LOGGER.debug(
            f'\t---> Была вызвана функция {func.__name__} c параметрами {args}, {kwargs}. '
            f'Вызов из модуля {func.__module__}.'
            f'Вызов из функции {inspect.stack()[1][3]}', stacklevel=2)
        return result

    return deco


class ClientWorker:
    def __init__(self):
        pass

    def create_presence(self, account_name=settings.GUEST_USER):
        """
        Метод генерирует запрос о присутствии клиента
        :param account_name:
        :return:
        """
        # {
        #   'action': 'presence',
        #   'time': 1573760672.167031,
        #   'user': {
        #       'account_name': 'Guest'
        #   }
        # }
        out = {
            settings.ACTION: settings.PRESENCE,
            settings.TIME: time.time(),
            settings.USER: {
                settings.ACCOUNT_NAME: account_name
            }
        }
        return out

    def process_ans(self, message):
        """
        Метод разбирает ответ сервера
        :param message:
        :return:
        """
        if settings.RESPONSE in message:
            if message[settings.RESPONSE] == HTTPStatus.HTTP_200_OK:
                return f'{HTTPStatus.HTTP_200_OK} : OK'
            return f'{HTTPStatus.HTTP_400_BAD_REQUEST} : {message[settings.ERROR]}'
        raise ValueError
