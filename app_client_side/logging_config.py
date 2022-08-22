"""Кофнфиг клиентского логгера"""

import os

from common import settings
from common.services import GetLogger


class GetServerLogger(GetLogger):
    """ Служит для определения и инициализации логгера северной стороны. """
    logger_dir = os.path.join(settings.BASE_DIR,
                              r'app_client_side\logs\client.log')

    def _add_handlers(self):
        """ Создаём регистратор и настраиваем его. """
        self.logger.addHandler(self._get_stderr_handler())
        self.logger.addHandler(self._get_simple_file_handler())


CLIENT_LOGGER = GetServerLogger(logger_name='client_logger').get_logger()

# отладка
if __name__ == '__main__':
    CLIENT_LOGGER.critical('Критическая ошибка')
    CLIENT_LOGGER.error('Ошибка')
    CLIENT_LOGGER.debug('Отладочная информация')
    CLIENT_LOGGER.info('Информационное сообщение')
