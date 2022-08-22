import time
import unittest

from common import settings
from common.services import HTTPStatus
from app_server_side.services import ServerWorker

class TestServerServices(unittest.TestCase):

    def setUp(self) -> None:
        self.server_worker = ServerWorker()
        self.error_response = {
            settings.RESPONSE: HTTPStatus.HTTP_400_BAD_REQUEST,
            settings.ERROR: 'Bad Request'
        }
        self.ok_response = {
            settings.RESPONSE: HTTPStatus.HTTP_200_OK
        }
        self.testing_time = time.time()

    def test_no_action(self):
        """Ошибка если нет действия. """
        self.assertEqual(
            self.server_worker.process_client_message(
                {
                    settings.TIME: self.testing_time,
                    settings.USER: {settings.ACCOUNT_NAME: settings.GUEST_USER}
                }
            ),
            self.error_response)

    def test_wrong_action(self):
        """Ошибка если неизвестное действие. """
        self.assertEqual(
            self.server_worker.process_client_message(
                {
                    settings.ACTION: 'Wrong',
                    settings.TIME: self.testing_time,
                    settings.USER: {settings.ACCOUNT_NAME: settings.GUEST_USER}
                }
            ),
            self.error_response
        )

    def test_no_time(self):
        """Ошибка, если  запрос не содержит штампа времени. """
        self.assertEqual(
            self.server_worker.process_client_message(
                {
                    settings.ACTION: settings.PRESENCE,
                    settings.USER: {settings.ACCOUNT_NAME: settings.GUEST_USER}
                }
            ),
            self.error_response
        )

    def test_no_user(self):
        """Ошибка - нет пользователя. """
        self.assertEqual(
            self.server_worker.process_client_message(
                {
                    settings.ACTION: settings.PRESENCE,
                    settings.TIME: self.testing_time
                }
            ),
            self.error_response
        )

    def test_unknown_user(self):
        """Ошибка - не Guest. """
        self.assertEqual(
            self.server_worker.process_client_message(
                {
                    settings.ACTION: settings.PRESENCE,
                    settings.TIME: self.testing_time,
                    settings.USER: {settings.ACCOUNT_NAME: 'Another_User'}
                }
            ),
            self.error_response
        )

    def test_ok_check(self):
        """Корректный запрос. """
        self.assertEqual(
            self.server_worker.process_client_message(
                {
                    settings.ACTION: settings.PRESENCE,
                    settings.TIME: self.testing_time,
                    settings.USER: {settings.ACCOUNT_NAME: settings.GUEST_USER}
                }
            ),
            self.ok_response
        )


if __name__ == '__main__':
    unittest.main()
