"""Кофнфиг серверного логгера"""

import os

from common import settings
from common.services import GetLogger


class GetServerLogger(GetLogger):
    """ Служит для определения и инициализации логгера северной стороны. """
    logger_dir = os.path.join(settings.BASE_DIR,
                              r'app_server_side\logs\server.log')


SERVER_LOGGER = GetServerLogger(logger_name='server_logger').get_logger()

# отладка
if __name__ == '__main__':
    SERVER_LOGGER.critical('Критическая ошибка')
    SERVER_LOGGER.error('Ошибка')
    SERVER_LOGGER.debug('Отладочная информация')
    SERVER_LOGGER.info('Информационное сообщение')
