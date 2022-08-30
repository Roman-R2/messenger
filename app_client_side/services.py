"""
Содержит сервисные классы и функции
"""
import argparse
import inspect
import logging
import sys
import time

from common import settings
from common.services import HTTPStatus, CLIArguments

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


class ClientCLIArguments(CLIArguments):
    parser_description = 'Запуск по параметрам -p порт -a адрес -m режим'

    def __init__(self):
        super().__init__()
        self._add_mode_argument()

    def _add_mode_argument(self):
        self.parser.add_argument(
            '-m',
            type=str,
            help="Укажите режим для клиента (send или listen)",
            default='listen',
            required=False
        )

    def get_connect_params(self):
        super_connect_params = super().get_connect_params()
        args = self.parser.parse_args()
        if args.m:
            self.mode = args.m
            self._check_client_mode()

        return super_connect_params[0], super_connect_params[1], self.mode

    def _check_client_mode(self):
        if self.mode not in ('send', 'listen'):
            print(
                'В качастве режима клиента должен быть указан send или listen.'
            )
            sys.exit(1)


class ClientWorker:
    def __init__(self):
        pass

    @debug_logger
    def create_presence(self, account_name=settings.GUEST_USER):
        """
        Метод генерирует запрос о присутствии клиента
        :param account_name:
        :return:
        """
        out = {
            settings.ACTION: settings.PRESENCE,
            settings.TIME: time.time(),
            settings.USER: {
                settings.ACCOUNT_NAME: account_name
            }
        }
        return out

    @debug_logger
    def process_ans(self, message):
        """
        Метод разбирает ответ сервера
        :param message:
        :return:
        """
        if settings.ACTION in message:
            if message[settings.HTTP_STATUS] == HTTPStatus.HTTP_200_OK:
                return f'{HTTPStatus.HTTP_200_OK} : {settings.OK}'
            return f'{HTTPStatus.HTTP_400_BAD_REQUEST} : {message[settings.ERROR]}'
        raise ValueError

    @debug_logger
    def create_message(self, sock, account_name=settings.GUEST_USER):
        """Функция запрашивает текст сообщения и возвращает его.
        Так же завершает работу при вводе подобной комманды
        """
        message = input(
            'Введите сообщение для отправки или \'!exit\' для завершения работы: ')
        if message == '!exit':
            sock.close()
            CLIENT_LOGGER.info('Завершение работы по команде пользователя.')
            print('Спасибо за использование нашего сервиса!')
            sys.exit(0)
        message_dict = {
            settings.ACTION: settings.MESSAGE,
            settings.TIME: time.time(),
            settings.ACCOUNT_NAME: account_name,
            settings.MESSAGE_TEXT: message
        }
        CLIENT_LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')
        return message_dict

    def __check_message_from_server(self, server_message: dict):
        """
        Проверит сообщение от клиента на корректность.
        :param client_message:
        :return:
        """
        # Если нет ключа action - то ошибка
        if settings.ACTION not in server_message:
            return False
        if settings.ACCOUNT_NAME not in server_message:
            return False
        if settings.MESSAGE_TEXT not in server_message:
            return False
        if server_message[settings.ACTION] != settings.MESSAGE:
            return False
        return True

    def __check_user_presence(self, server_message: dict):
        if settings.ACTION not in server_message:
            return False
        if settings.ACCOUNT_NAME not in server_message:
            return False
        if settings.MESSAGE_TEXT not in server_message:
            return False
        if server_message[settings.ACTION] != settings.RESPONSE:
            return False
        return True

    @debug_logger
    def message_from_server(self, message):
        """ Функция - обработчик сообщений других пользователей, поступающих с сервера. """
        if self.__check_user_presence(message):
            print('---> ', message[settings.MESSAGE_TEXT])
        elif self.__check_message_from_server(message):
            print(f'Получено сообщение от пользователя '
                  f'{message[settings.ACCOUNT_NAME]}: {message[settings.MESSAGE_TEXT]}')
            CLIENT_LOGGER.info(f'Получено сообщение от пользователя '
                               f'{message[settings.ACCOUNT_NAME]}:\n{message[settings.MESSAGE_TEXT]}')
        else:
            CLIENT_LOGGER.error(
                f'Получено некорректное сообщение с сервера: {message}')
