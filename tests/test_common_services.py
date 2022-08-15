import json
import time
import unittest

from common import settings
from common.services import HTTPStatus, Message


class TestSocket:
    """
    Тестовый класс для тестирования отправки и получения,
    при создании требует словарь, который будет прогонятся
    через тестовую функцию
    """

    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_message = None
        self.received_message = None

    def send(self, message_to_send):
        """
        Тестовая функция отправки, корретно  кодирует сообщение,
        так-же сохраняет что должно было отправлено в сокет.
        message_to_send - то, что отправляем в сокет
        :param message_to_send:
        :return:
        """
        json_test_message = json.dumps(self.test_dict)
        # кодирует сообщение
        self.encoded_message = json_test_message.encode(settings.ENCODING)
        # сохраняем что должно было отправлено в сокет
        self.received_message = message_to_send

    def recv(self, max_len):
        """
        Получаем данные из сокета
        :param max_len:
        :return:
        """
        json_test_message = json.dumps(self.test_dict)
        return json_test_message.encode(settings.ENCODING)


class TestCommonServices(unittest.TestCase):

    def setUp(self) -> None:
        testing_time = time.time()

        self.test_dict_send = {
            settings.ACTION: settings.PRESENCE,
            settings.TIME: testing_time,
            settings.USER: {
                settings.ACCOUNT_NAME: 'test_test'
            }
        }
        self.test_dict_receive_ok = {
            settings.RESPONSE: HTTPStatus.HTTP_200_OK
        }
        self.test_dict_receive_err = {
            settings.RESPONSE: HTTPStatus.HTTP_400_BAD_REQUEST,
            settings.ERROR: HTTPStatus.TEXT_STATUS_400
        }

    def test_send_message(self):
        """
        Тестируем корректность работы фукции отправки,
        создадим тестовый сокет и проверим корректность отправки словаря
        :return:
        """
        # экземпляр тестового словаря, хранит собственно тестовый словарь
        # экземпляр тестового словаря, хранит собственно тестовый словарь
        test_socket = TestSocket(self.test_dict_send)
        # вызов тестируемой функции, результаты будут сохранены в тестовом сокете
        Message.send(test_socket, self.test_dict_send)
        # проверка корретности кодирования словаря.
        # сравниваем результат довренного кодирования и результат от тестируемой функции
        self.assertEqual(
            test_socket.encoded_message,
            test_socket.received_message
        )
        # дополнительно, проверим генерацию исключения, при не словаре на входе.
        with self.assertRaises(Exception):
            Message.send(test_socket, test_socket)

    def test_get_message(self):
        """
        Тест функции приёма сообщения
        :return:
        """
        test_sock_ok = TestSocket(self.test_dict_receive_ok)
        test_sock_err = TestSocket(self.test_dict_receive_err)
        # тест корректной расшифровки корректного словаря
        self.assertEqual(
            Message.receive(test_sock_ok),
            self.test_dict_receive_ok
        )
        # тест корректной расшифровки ошибочного словаря
        self.assertEqual(
            Message.receive(test_sock_err),
            self.test_dict_receive_err
        )


if __name__ == '__main__':
    unittest.main()
