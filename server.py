"""
Серверный скрипт.
"""

import socket
import json

from common import settings
from common.services import CLIArguments, ServerWorker, Message

if __name__ == '__main__':
    cli_arg_obj = CLIArguments()
    connect_params = cli_arg_obj.get_connect_params()
    print(f'Получены адрес {connect_params[0]} порт {connect_params[1]}')

    # Готовим сокет
    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind(connect_params)

    # Слушаем порт
    transport.listen(settings.MAX_CONNECTIONS)

    server_worker = ServerWorker()

    while True:
        client_socket_object, address_info = transport.accept()
        try:
            message_from_client = Message.receive(client_socket_object)
            # {'action': 'presence', 'time': 1573760672.167031, 'user': {'account_name': 'Guest'}}
            response = server_worker.process_client_message(
                message_from_client
            )
            Message.send(client_socket_object, response)
            client_socket_object.close()
        except (ValueError, json.JSONDecodeError):
            print('Принято некорректное сообщение от клиента.')
            client_socket_object.close()
