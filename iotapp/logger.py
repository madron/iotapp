import logging
import sys


class LoggerMixin:
    def get_logger(self, level=None, name=__name__):
        log_level = dict(
            debug=logging.DEBUG,
            info=logging.INFO,
            warning=logging.WARNING,
            error=logging.ERROR,
        )
        level = level or getattr(self, 'log_level', None) or os.environ.get('LOG_LEVEL', 'info')
        logger = logging.getLogger(name)
        logger.setLevel(log_level[level])
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(levelname)-8s %(name)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
