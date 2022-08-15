"""
Содержит сервисные классы и функции
"""

from common import settings
from common.services import HTTPStatus


class ServerWorker:
    def __init__(self):
        pass

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
        if client_message[settings.USER][settings.ACCOUNT_NAME] != settings.GUEST_USER:
            return False
        return True

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
