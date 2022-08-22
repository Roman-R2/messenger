"""
Клиентский скрипт.
"""

import json
import logging
import socket

from app_client_side.services import ClientWorker
from common.services import CLIArguments, Message

from app_client_side import logging_config

# Инициализация логирования сервера.
CLIENT_LOGGER = logging.getLogger('client_logger')


def debug_logger(func):
    def deco(*args, **kwargs):
        result = func(*args, **kwargs)
        CLIENT_LOGGER.debug(
            f'\t--->\t Запущен: {func.__name__}. Аннотация:'
            f' {func.__annotations__}. '
            f'Резулитат: {result}'
        )
        return result

    return deco


@debug_logger
class ClientSocket:
    def __init__(self, connect_params_list):
        self.connect_params_list = connect_params_list
        self.__start_socket()

    @debug_logger
    def __start_socket(self):
        # Готовим сокет
        self.transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.transport.connect(connect_params)

    @debug_logger
    def get_transport(self):
        return self.transport


if __name__ == '__main__':
    '''Загружаем параметы коммандной строки'''
    # client.py 192.168.1.2 8079
    cli_arg_obj = CLIArguments()
    connect_params = cli_arg_obj.get_connect_params()
    print(f'Получены адрес {connect_params[0]} порт {connect_params[1]}')

    # Получим транспорт
    transport = ClientSocket(connect_params).get_transport()

    client_worker = ClientWorker()

    message_to_server = client_worker.create_presence()
    CLIENT_LOGGER.debug(
        f'Сгенерировано сообщение для сервера: {message_to_server}'
    )
    Message.send(transport, message_to_server)
    CLIENT_LOGGER.debug(
        f'Отправлено сообщение на сервер {transport}'
    )
    try:
        answer = client_worker.process_ans(Message.receive(transport))
        CLIENT_LOGGER.debug(
            f'Разобран ответ от сервера: {answer}'
        )
    except (ValueError, json.JSONDecodeError):
        CLIENT_LOGGER.error(
            f'Не удалось декодировать сообщение сервера. Ошибка '
            f'json.JSONDecodeError.'
        )
