import logging
import os
import sys


class LoggerMixin:
    def get_logger(self, level=None, name=''):
        log_level = dict(
            debug=logging.DEBUG,
            info=logging.INFO,
            warning=logging.WARNING,
            error=logging.ERROR,
        )
        level = level or getattr(self, 'log_level', None) or os.environ.get('LOG_LEVEL', 'info')
        logger_name = 'app'
        if name:
            logger_name = 'app.{}'.format(name)
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level[level])
        if not name:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter('%(levelname)-8s %(name)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    def set_logger(self, name=''):
        self.logger = self.get_logger(name=name)
