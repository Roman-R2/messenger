"""
Клиентский скрипт.
"""
import json
import logging
import socket
import sys
import threading
import time

from app_client_side.services import ClientWorker, debug_logger, \
    ClientCLIArguments
from common.errors import ServerError, ReqFieldMissingError
from common.services import Message, CLIArguments

from app_client_side import logging_config

# Инициализация логирования сервера.
CLIENT_LOGGER = logging.getLogger('client_logger')


def show_connection_params(this_connect_params):
    print(' Параметры соединения '.center(70, '-'))
    print(
        f'\tадрес {this_connect_params[0]} \n\tпорт {this_connect_params[1]} \n\tимя {this_connect_params[2]}'
    )
    print(''.center(70, '-'))


@debug_logger
class ClientSocket:
    def __init__(self, connect_params_list):
        self.connect_params_list = connect_params_list
        self.__start_socket()

    @debug_logger
    def __start_socket(self):
        # Готовим сокет
        self.transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.transport.connect(self.connect_params_list)

    @debug_logger
    def get_transport(self):
        return self.transport


if __name__ == '__main__':
    '''Загружаем параметы коммандной строки'''
    # client.py 192.168.1.2 8079
    cli_arg_obj = ClientCLIArguments()
    connect_address, connect_port, client_name = cli_arg_obj.get_connect_params()
    show_connection_params((connect_address, connect_port, client_name))

    # Получим транспорт
    transport = ClientSocket(
        (connect_address, connect_port)
    ).get_transport()

    client_worker = ClientWorker()

    message_to_server = client_worker.create_presence(account_name=client_name)
    CLIENT_LOGGER.debug(
        f'Сгенерировано сообщение для сервера: {message_to_server}'
    )
    # print(f'Сгенерировано сообщение для сервера: {message_to_server}')
    Message.send(transport, message_to_server)
    CLIENT_LOGGER.debug(
        f'Отправлено сообщение на сервер {transport}'
    )
    # print(f'Отправлено сообщение на сервер {transport}')
    try:
        rcv_message = Message.receive(transport)
        # print(f'{rcv_message=}')
        answer = client_worker.process_ans(rcv_message)
        # print(f'{answer=}')
        CLIENT_LOGGER.debug(
            f'Разобран ответ от сервера: {answer}'
        )
    # except (ValueError, json.JSONDecodeError):
    #     CLIENT_LOGGER.error(
    #         f'Не удалось декодировать сообщение сервера. Ошибка '
    #         f'json.JSONDecodeError.'
    #     )
    except ServerError as error:
        CLIENT_LOGGER.error(
            f'При установке соединения сервер вернул ошибку: {error.text}'
        )
        sys.exit(1)
    except ReqFieldMissingError as missing_error:
        CLIENT_LOGGER.error(
            f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
        sys.exit(1)
    except ConnectionRefusedError:
        CLIENT_LOGGER.critical(
            f'Не удалось подключиться к серверу {connect_address}:{connect_port}, '
            f'конечный компьютер отверг запрос на подключение.')
        sys.exit(1)
    else:

        # Если соединение с сервером установлено корректно,
        # запускаем клиенский процесс приёма сообщний
        receiver = threading.Thread(
            target=client_worker.message_from_server,
            args=(transport, client_name),
            daemon=True
        )
        receiver.start()

        # затем запускаем отправку сообщений и взаимодействие с пользователем.
        user_interface = threading.Thread(
            target=client_worker.user_interactive,
            args=(transport, client_name),
            daemon=True
        )
        user_interface.start()
        CLIENT_LOGGER.debug('Запущены процессы')

        # Watchdog основной цикл, если один из потоков завершён,
        # то значит или потеряно соединение или пользователь
        # ввёл exit. Поскольку все события обработываются в потоках,
        # достаточно просто завершить цикл.
        while True:
            time.sleep(1)
            if receiver.is_alive() and user_interface.is_alive():
                continue
            break

        # # основной цикл прогрммы:
        # while True:
        #     # режим работы - отправка сообщений
        #     if client_mode == 'send':
        #         try:
        #             Message.send(
        #                 transport,
        #                 client_worker.create_message(transport)
        #             )
        #         except (
        #                 ConnectionResetError, ConnectionError,
        #                 ConnectionAbortedError):
        #             CLIENT_LOGGER.error(
        #                 f'Соединение с сервером {connect_address} было потеряно.')
        #             sys.exit(1)
        #
        #     # Режим работы приём:
        #     if client_mode == 'listen':
        #         try:
        #             client_worker.message_from_server(
        #                 Message.receive(transport))
        #         except (
        #                 ConnectionResetError, ConnectionError,
        #                 ConnectionAbortedError):
        #             CLIENT_LOGGER.error(
        #                 f'Соединение с сервером {connect_address} было потеряно.')
        #             sys.exit(1)
