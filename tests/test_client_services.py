import time
import unittest

from app_client_side.services import ClientWorker
from common import settings
from common.services import HTTPStatus


class TestClientServices(unittest.TestCase):

    def setUp(self) -> None:
        self.client_worker = ClientWorker()

    def test_def_presense(self):
        """Тест коректного запроса присутствия клиента"""
        testing_time = time.time()
        account_name = 'Guest'

        test_presence = self.client_worker.create_presence(
            account_name=account_name)
        # время необходимо приравнять принудительно
        # иначе тест никогда не будет пройден
        test_presence[settings.TIME] = testing_time

        self.assertEqual(1, 1)
        self.assertEqual(
            test_presence,
            {
                settings.ACTION: settings.PRESENCE,
                settings.TIME: testing_time,
                settings.USER: {
                    settings.ACCOUNT_NAME: account_name
                }
            }
        )

    def test_200_ans(self):
        """Тест корректтного разбора ответа 200"""
        self.assertEqual(
            self.client_worker.process_ans(
                {settings.RESPONSE: HTTPStatus.HTTP_200_OK}
            ),
            f'{HTTPStatus.HTTP_200_OK} : OK'
        )

    def test_400_ans(self):
        """Тест корректного разбора 400"""
        self.assertEqual(
            self.client_worker.process_ans(
                {
                    settings.RESPONSE: HTTPStatus.HTTP_400_BAD_REQUEST,
                    settings.ERROR: 'Bad Request'
                }
            ),
            f'{HTTPStatus.HTTP_400_BAD_REQUEST} : Bad Request'
        )

    def test_no_response(self):
        """Тест исключения без поля RESPONSE"""
        self.assertRaises(
            ValueError,
            self.client_worker.process_ans,
            {settings.ERROR: 'Bad Request'}
        )


if __name__ == '__main__':
    unittest.main()
