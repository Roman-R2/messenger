"""
Содержит сервисные классы и функции
"""
import argparse
import json
import socket
import sys

from common import settings


class HTTPStatus:
    HTTP_200_OK = 200
    HTTP_400_BAD_REQUEST = 400

    TEXT_STATUS_400 = 'Bad Request'


class CLIArguments:
    def __init__(self):
        self.port = settings.DEFAULT_PORT
        self.address = settings.DEFAULT_IP_ADDRESS
        self.parser = argparse.ArgumentParser(
            description='Запуск по параметрам -p порт -a адрес'
        )
        self.__add_port_argument()
        self.__add_address_argument()

    def __add_port_argument(self):
        self.parser.add_argument(
            '-p',
            type=int,
            help="Укажите порт сервера",
            required=False
        )

    def __add_address_argument(self):
        self.parser.add_argument(
            '-a',
            type=str,
            help="Укажите ip адрес сервера",
            required=False
        )

    def get_connect_params(self):
        """ Вернет кортеж из порта и адреса. """
        args = self.parser.parse_args()
        if args.p:
            self.port = args.p
            self.check_port()
        if args.a:
            self.address = args.a
            self.check_ip_address()
        return self.address, self.port

    def check_port(self):
        """ Проверит порт на корректность. """
        if self.port < 1024 or self.port > 65535:
            print(
                'В качастве порта может быть указано только число в диапазоне от 1024 до 65535.'
            )
            sys.exit(1)

    def check_ip_address(self):
        """ Проверит ip адрес на корректность. """
        if not (self.address.count('.') == 3 and all(
                [
                    num.isdigit() and 0 <= int(num) <= 256
                    for num in self.address.split('.')
                ]
        )):
            print(
                'В качастве адреса должен быть указан валидный ip адрес.'
            )
            sys.exit(1)


class Message:
    """ Класс для работы с сообщениями, их приема и передачи. """

    def __init__(self, socket_object: socket.socket):
        self.socket_object = socket_object

    def __receive(self):
        """
        Метод приёма и декодирования сообщения
        принимает байты выдаёт словарь, если принято
        что-то другое отдаёт ошибку значения
        :return:
        """
        encoded_response = self.socket_object.recv(settings.MAX_PACKAGE_LENGTH)
        if not isinstance(encoded_response, bytes):
            raise ValueError

        json_response = encoded_response.decode(settings.ENCODING)
        response = json.loads(json_response)

        if not isinstance(response, dict):
            raise ValueError

        return response

    def __send(self, dict_message):
        """
        Утилита кодирования и отправки сообщения
        принимает словарь и отправляет его
        :param dict_message:
        :return:
        """
        js_message = json.dumps(dict_message)
        encoded_message = js_message.encode(settings.ENCODING)
        self.socket_object.send(encoded_message)

    @staticmethod
    def receive(socket_object):
        return Message(socket_object).__receive()

    @staticmethod
    def send(socket_object, dict_message):
        return Message(socket_object).__send(dict_message)
