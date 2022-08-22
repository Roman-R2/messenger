"""
Содержит сервисные классы и функции
"""
import argparse
import json
import logging
import logging.handlers
import os
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


class GetLogger:
    """ Служит для определения и инициализации логгера северной стороны. """

    logger_format = '%(asctime)s %(levelname)s %(filename)s %(message)s'
    logger_dir = os.path.join(
        settings.BASE_DIR,
        r'app_server_side\logs\server.log'
    )

    def __init__(self, logger_name='server'):
        # создаём формировщик логов (formatter):
        self.server_formatter = logging.Formatter(self.logger_format)
        # Подготовка имени файла для логирования
        self.logger = logging.getLogger(logger_name)
        self._add_handlers()
        self.logger.setLevel(settings.LOGGING_LEVEL)

    def _get_stderr_handler(self):
        """ Создаст поток вывода логов в поток вывода ошибок. """
        stream_handler = logging.StreamHandler(sys.stderr)
        stream_handler.setFormatter(self.server_formatter)
        stream_handler.setLevel(logging.ERROR)
        return stream_handler

    def _get_rotating_file_handler(self):
        """ Создаст поток вывода логов в файл. """
        log_file = logging.handlers.TimedRotatingFileHandler(
            self.logger_dir,
            encoding=settings.ENCODING,
            interval=1,
            when='D'
        )
        log_file.setFormatter(self.server_formatter)
        return log_file

    def _get_simple_file_handler(self):
        log_file = logging.FileHandler(
            self.logger_dir,
            encoding=settings.ENCODING
        )
        log_file.setFormatter(self.server_formatter)
        return log_file

    def _add_handlers(self):
        """ Создаём регистратор и настраиваем его. """
        self.logger.addHandler(self._get_stderr_handler())
        self.logger.addHandler(self._get_rotating_file_handler())

    def get_logger(self):
        return self.logger
