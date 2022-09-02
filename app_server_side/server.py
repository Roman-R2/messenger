"""
Серверный скрипт.
"""
import logging
import socket
import json

# Инициализация логирования сервера.
import time

import select

from app_client_side.services import debug_logger
from app_server_side.services import ServerWorker
from common import settings
from common.services import CLIArguments, Message, HTTPStatus

import logging_config

SERVER_LOGGER = logging.getLogger('server_logger')


def show_connection_params(this_connect_params):
    print(' Параметры для соединения '.center(70, '-'))
    print(
        f'\tадрес {this_connect_params[0]} \n\tпорт {this_connect_params[1]}'
    )
    print(''.center(70, '-'))


class ServerSocket:
    def __init__(self, connect_params_list):
        self.connect_params_list = connect_params_list
        self.__start_socket()

    @debug_logger
    def __start_socket(self):
        # Готовим сокет
        self.transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.transport.bind(self.connect_params_list)
        self.transport.settimeout(1)
        # Слушаем порт
        self.transport.listen(settings.MAX_CONNECTIONS)

    @debug_logger
    def get_transport(self):
        return self.transport


if __name__ == '__main__':
    cli_arg_obj = CLIArguments()
    connect_params = cli_arg_obj.get_connect_params()
    show_connection_params(connect_params)

    server_worker = ServerWorker()

    # список клиентов , очередь сообщений
    clients = []
    messages = []

    # Словарь, содержащий имена пользователей и соответствующие им сокеты.
    names = dict()

    while True:
        try:
            client_socket_object, address_info = ServerSocket(
                connect_params
            ).get_transport().accept()
        except OSError:
            pass
        else:
            SERVER_LOGGER.info(f'Установлено соедение с ПК {address_info}')
            clients.append(client_socket_object)

        recv_data_lst = []
        send_data_lst = []
        err_lst = []

        # Проверяем на наличие ждущих клиентов
        try:
            if clients:
                recv_data_lst, send_data_lst, err_lst = select.select(clients,
                                                                      clients,
                                                                      [], 0)
                # print(f'{recv_data_lst=}')
                # print(f'{send_data_lst=}')
                # print(f'{err_lst=}')
        except OSError:
            pass

        # принимаем сообщения и если там есть сообщения,
        # кладём в словарь, если ошибка, исключаем клиента.
        if recv_data_lst:
            for client_with_message in recv_data_lst:
                try:
                    receive_message = Message.receive(client_with_message)
                    print(' Получили сообщение '.center(69, '-'))
                    print(f'{receive_message=}')

                    processed_client_message, message_type = server_worker.process_client_message(
                        receive_message
                    )
                    print(f'{message_type=} {processed_client_message= }')
                    # Если сервер подготовил ответ на присутствие клиента,
                    # то добавляем его в names для отслеживания,
                    # если это сообщение, то в массив сообщений,
                    # а если ошибка, то логируем
                    print('-'.center(69, '-'))
                    if message_type == settings.RESPONSE:
                        print(settings.PRESENCE)
                        print(
                            f'{processed_client_message[settings.SENDER]=}'
                        )
                        print(f'{client_with_message=}')
                        names[processed_client_message[
                            settings.SENDER]] = client_with_message
                        Message.send(client_with_message, processed_client_message)
                        print(f'{names=}')
                    elif message_type == settings.MESSAGE:
                        messages.append(processed_client_message)
                    elif message_type == settings.ERROR:
                        SERVER_LOGGER.error(
                            f'Не распознано сообщение от клиента {client_with_message}')
                except:
                    SERVER_LOGGER.info(
                        f'Клиент {client_with_message.getpeername()} '
                        f'отключился от сервера.')
                    clients.remove(client_with_message)


        # Если есть сообщения для отправки и ожидающие клиенты, отправляем им сообщение.
        if messages and send_data_lst:
            print(f'{messages=}')
            print(f'{send_data_lst=}')
            print(f'{names=}')
            message = messages[0]

            # Если получатель найден в словаре подключенных пользователей
            print(f'{settings.RECEIVER=}')
            print(f'{names.keys()=}')
            if message[settings.RECEIVER] in names.keys():
                try:
                    Message.send(names[message[settings.RECEIVER]], message)
                    del messages[0]
                except:
                    SERVER_LOGGER.info(
                        f'Клиент {names[message[settings.RECEIVER]].getpeername()} отключился от сервера.')
                    clients.remove(names[message[settings.RECEIVER]])
            else:
                # Если не нашли никнейм пользователя в списке подключенных клиентов
                Message.send(
                    names[message[settings.SENDER]],
                    {
                        'action': settings.ERROR,
                        'http_status': HTTPStatus.HTTP_404_NOT_FOUND,
                        'sender_nickname': 'server',
                        'receiver_nickname': message[settings.SENDER],
                        'message_text': f'Пользователь с данным ником {message[settings.RECEIVER]} не подключен к серверу',
                        'error_text': f'Пользователь с данным ником {message[settings.RECEIVER]}  не подключен к серверу'}
                )
                del messages[0]



            # for waiting_client in send_data_lst:
            #     try:
            #         Message.send(waiting_client, message)
            #     except:
            #         SERVER_LOGGER.info(
            #             f'Клиент {waiting_client.getpeername()} отключился от сервера.')
            #         clients.remove(waiting_client)
