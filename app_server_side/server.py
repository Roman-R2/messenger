"""
Серверный скрипт.
"""
import logging
import socket
import json

from app_server_side.services import ServerWorker, debug_logger
from common import settings
from common.services import CLIArguments, Message

import logging_config
# Инициализация логирования сервера.
SERVER_LOGGER = logging.getLogger('server_logger')


class ServerSocket:
    def __init__(self, connect_params_list):
        self.connect_params_list = connect_params_list
        self.__start_socket()

    @debug_logger
    def __start_socket(self):
        # Готовим сокет
        self.transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.transport.bind(self.connect_params_list)
        # Слушаем порт
        self.transport.listen(settings.MAX_CONNECTIONS)

    @debug_logger
    def get_transport(self):
        return self.transport


if __name__ == '__main__':
    cli_arg_obj = CLIArguments()
    connect_params = cli_arg_obj.get_connect_params()
    print(f'Получены адрес {connect_params[0]} порт {connect_params[1]}')

    server_worker = ServerWorker()

    while True:
        client_socket_object, address_info = ServerSocket(
            connect_params
        ).get_transport().accept()
        try:
            message_from_client = Message.receive(client_socket_object)
            SERVER_LOGGER.debug(
                f'Получили сообщение от клиента: {message_from_client}.'
            )
            # {'action': 'presence', 'time': 1573760672.167031, 'user': {'account_name': 'Guest'}}
            response = server_worker.process_client_message(
                message_from_client
            )
            SERVER_LOGGER.debug(
                f'Обработали сообщение от клиента{message_from_client}'
                f'. Ответ: {response}.'
            )
            print(response)
            Message.send(client_socket_object, response)
            SERVER_LOGGER.debug(
                f'Отправили сообщение клиенту'
            )
            client_socket_object.close()
            SERVER_LOGGER.debug(
                f'Закрыли сокет'
            )
        except (ValueError, json.JSONDecodeError):
            # print('Принято некорректное сообщение от клиента.')
            SERVER_LOGGER.error(
                f'Принято некорректное сообщение от клиента. Ошибка '
                f'json.JSONDecodeError.'
            )
            SERVER_LOGGER.debug(
                f'Закрыли сокет'
            )
            client_socket_object.close()
