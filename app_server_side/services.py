"""
Содержит сервисные классы и функции
"""
import inspect
import logging
from pprint import pprint

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
    def __is_presence_message(self, client_message: dict):
        """
        Проверит что это корректное сообщение присутствия.
        :param client_message:
        :return:
        """
        # Если нет ключа action - то ошибка
        if settings.ACTION not in client_message:
            return False
        if settings.TIME not in client_message:
            return False
        if settings.SENDER not in client_message:
            return False
        if client_message[settings.ACTION] != settings.PRESENCE:
            return False
        # if client_message[settings.USER][
        #     settings.ACCOUNT_NAME] != settings.GUEST_USER:
        #     return False
        return True

    @debug_logger
    def __is_text_message(self, client_message: dict):
        """
        Проверит что это корректное текстовое сообщение от клиента.
        :param client_message:
        :return:
        """
        # Если нет ключа action - то ошибка
        if settings.ACTION not in client_message:
            return False
        if settings.TIME not in client_message:
            return False
        if settings.MESSAGE_TEXT not in client_message:
            return False
        if client_message[settings.ACTION] != settings.MESSAGE:
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
        print(f'{client_message=}')
        if self.__is_presence_message(client_message):
            print('__is_presence_message')
            return {
                       settings.ACTION: settings.RESPONSE,
                       settings.HTTP_STATUS: HTTPStatus.HTTP_200_OK,
                       settings.SENDER: client_message[settings.SENDER],
                       settings.MESSAGE_TEXT: f'Сервер: Подключение клиента {client_message[settings.SENDER]}...',
                       settings.ERROR_TEXT: ''
                   }, settings.RESPONSE
        elif self.__is_text_message(client_message):
            return {
                       settings.ACTION: settings.MESSAGE,
                       settings.HTTP_STATUS: HTTPStatus.HTTP_200_OK,
                       settings.SENDER: client_message[
                           settings.SENDER],
                       settings.RECEIVER: client_message[
                           settings.RECEIVER],
                       settings.MESSAGE_TEXT: client_message[
                           settings.MESSAGE_TEXT],
                       settings.ERROR_TEXT: ''
                   }, settings.MESSAGE

        return {
                   settings.ACTION: settings.ERROR,
                   settings.HTTP_STATUS: HTTPStatus.HTTP_400_BAD_REQUEST,
                   settings.SENDER: '',
                   settings.MESSAGE_TEXT: '',
                   settings.ERROR_TEXT: f'Запрос не опознан. Статус {HTTPStatus.TEXT_STATUS_400}'
               }, settings.ERROR
