"""
Содержит сервисные классы и функции
"""
import argparse
import inspect
import json
import logging
import sys
import time

from common import settings
from common.services import HTTPStatus, CLIArguments, Message

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
    parser_description = 'Запуск по параметрам -p порт -a адрес -n имя клиента'

    def __init__(self):
        super().__init__()
        self._add_mode_argument()

    def _add_mode_argument(self):
        self.parser.add_argument(
            '-n',
            type=str,
            help="Укажите имя клиента",
            default='guest_' + str(int(time.time())),
            required=False
        )

    def get_connect_params(self):
        super_connect_params = super().get_connect_params()
        args = self.parser.parse_args()
        if args.n:
            self.name = args.n
            self._check_client_mode()

        return super_connect_params[0], super_connect_params[1], self.name

    def _check_client_mode(self):
        if not isinstance(self.name, str) and len(self.name) < 25:
            print(
                'Имя клиента должно быть строкой, длиной меньше 25 символов.'
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
            settings.SENDER: account_name
        }
        return out

    @debug_logger
    def process_ans(self, message):
        """
        Метод разбирает ответ сервера
        :param message:
        :return:
        """
        print(f'{message=}')
        if settings.ACTION in message:
            if message[settings.HTTP_STATUS] == HTTPStatus.HTTP_200_OK:
                return f'{HTTPStatus.HTTP_200_OK} : {settings.OK}'
            return f'{HTTPStatus.HTTP_400_BAD_REQUEST} : {message[settings.ERROR_TEXT]}'
        raise ValueError

    @debug_logger
    def create_message(self, sock, sender_nickname=settings.GUEST_USER):
        """Функция запрашивает текст сообщения и возвращает его.
        Так же завершает работу при вводе подобной комманды
        """
        to_user = input('Nickname, кому отправить сообщение: ')
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
            settings.SENDER: sender_nickname,
            settings.RECEIVER: to_user,
            settings.MESSAGE_TEXT: message
        }
        CLIENT_LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')
        return message_dict

    def show_help(self):
        """Функция выводящяя справку по использованию"""
        print('Поддерживаемые команды:')
        print(
            'message - отправить сообщение. Кому и текст будет запрошены отдельно.')
        print('exit - выход из программы')

    def create_exit_message(self, account_name):
        """Функция создаёт словарь с сообщением о выходе"""
        return {
            settings.ACTION: settings.EXIT,
            settings.TIME: time.time(),
            settings.ACCOUNT_NAME: account_name
        }

    @debug_logger
    def user_interactive(self, sock, username):
        """Функция взаимодействия с пользователем, запрашивает команды, отправляет сообщения"""
        self.show_help()
        while True:
            command = input('Введите команду: ')
            if command == 'message':

                Message.send(
                    sock,
                    self.create_message(sock, username)
                )
                # Это для того, что ели сервервернет ошибку, то строчка дебага успела вывистись до приглашения о введении команды
                time.sleep(1)
            elif command == 'exit':
                Message.send(
                    sock,
                    self.create_exit_message(username)
                )
                print('Завершение соединения.')
                CLIENT_LOGGER.info(
                    'Завершение работы по команде пользователя.')
                # Задержка неоходима, чтобы успело уйти сообщение о выходе
                time.sleep(1)
                break
            else:
                print('Команда не распознана.')

    def __is_correct_user_message(self, server_message: dict):
        """
        Проверит сообщение от клиента на корректность.
        :param client_message:
        :return:
        """
        # Если нет ключа action - то ошибка
        if settings.ACTION not in server_message:
            return False
        if settings.SENDER not in server_message:
            return False
        if settings.RECEIVER not in server_message:
            return False
        if settings.MESSAGE_TEXT not in server_message:
            return False
        if server_message[settings.ACTION] != settings.MESSAGE:
            return False
        return True

    def __is_correct_user_presence_message(self, server_message: dict):
        """  """
        if settings.ACTION not in server_message:
            return False
        if settings.ACCOUNT_NAME not in server_message:
            return False
        if settings.MESSAGE_TEXT not in server_message:
            return False
        if server_message[settings.ACTION] != settings.RESPONSE:
            return False
        return True

    def __is_server_error_message(self, server_message: dict):
        """ Проверим, что сообщение типа ошибки """
        if settings.ACTION not in server_message:
            return False
        if settings.ERROR_TEXT not in server_message:
            return False
        if server_message[settings.ACTION] != settings.ERROR:
            return False
        return True

    @debug_logger
    def message_from_server(self, sock, my_username):
        """ Функция - обработчик сообщений других пользователей, поступающих с сервера. """
        while True:
            message = Message.receive(sock)
            try:
                if self.__is_correct_user_presence_message(message):
                    print('---> ', message[settings.MESSAGE_TEXT])
                elif self.__is_correct_user_message(message):
                    info_message = f'Cообщение от пользователя {message[settings.SENDER]}: {message[settings.MESSAGE_TEXT]}'
                    print(info_message)
                    CLIENT_LOGGER.info(info_message)
                elif self.__is_server_error_message(message):
                    print(f'ERROR: {message[settings.ERROR_TEXT]}')
                    CLIENT_LOGGER.debug(f'Получено сообщение об ошибке от сервера {message}')
                else:
                    CLIENT_LOGGER.error(
                        f'Получено некорректное сообщение с сервера: {message}')
            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError, json.JSONDecodeError):
                CLIENT_LOGGER.critical(f'Потеряно соединение с сервером.')
                break
