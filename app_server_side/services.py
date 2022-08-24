"""
Содержит сервисные классы и функции
"""
import inspect
import logging

from common import settings
from common.services import HTTPStatus

from app_server_side import logging_config

# Инициализация логирования сервера.
SERVER_LOGGER = logging.getLogger('server_logger')


def debug_logger(func):
    def deco(*args, **kwargs):
        result = func(*args, **kwargs)
        SERVER_LOGGER.debug(
            f'\t---> Была вызвана функция {func.__name__} c параметрами {args}, {kwargs}. '
            f'Вызов из модуля {func.__module__}.'
            f'Вызов из функции {inspect.stack()[1][3]}', stacklevel=2)
        return result

    return deco


@debug_logger
class ServerWorker:
    def __init__(self):
        pass

    @debug_logger
    def __check_client_message(self, client_message: dict):
        """
        Проверит сообщение от клиента на корректность.
        :param client_message:
        :return:
        """
        # Если нет ключа action - то ошибка
        if settings.ACTION not in client_message:
            return False
        if settings.TIME not in client_message:
            return False
        if settings.USER not in client_message:
            return False
        if client_message[settings.ACTION] != settings.PRESENCE:
            return False
        if client_message[settings.USER][
            settings.ACCOUNT_NAME] != settings.GUEST_USER:
            return False
        return True

    @debug_logger
    def process_client_message(self, client_message: dict):
        """
        Обработчик сообщений от клиентов, принимает словарь -
        сообщение от клиента, проверяет корректность,
        возвращает словарь-ответ для клиента
        :param client_message:
        :return:
        """
        # print(f'{client_message=}')
        if self.__check_client_message(client_message):
            return {
                settings.RESPONSE: HTTPStatus.HTTP_200_OK
            }
        return {
            settings.RESPONSE: HTTPStatus.HTTP_400_BAD_REQUEST,
            settings.ERROR: HTTPStatus.TEXT_STATUS_400
        }
