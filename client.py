"""
Клиентский скрипт.
"""

import json
import socket

from common.services import CLIArguments, Message, ClientWorker

if __name__ == '__main__':
    '''Загружаем параметы коммандной строки'''
    # client.py 192.168.1.2 8079
    cli_arg_obj = CLIArguments()
    connect_params = cli_arg_obj.get_connect_params()
    print(f'Получены адрес {connect_params[0]} порт {connect_params[1]}')

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.connect(connect_params)

    client_worker = ClientWorker()

    message_to_server = client_worker.create_presence()
    Message.send(transport, message_to_server)
    try:
        answer = client_worker.process_ans(Message.receive(transport))
        print(answer)
    except (ValueError, json.JSONDecodeError):
        print('Не удалось декодировать сообщение сервера.')
