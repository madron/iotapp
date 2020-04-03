import unittest
from iotapp import test


class TestLoggerTest(unittest.TestCase):
    def test_debug(self):
        logger = test.TestLogger(level='debug')
        logger.debug('msg')
        self.assertEqual(logger.logged, [('debug', 'msg')])

    def test_info(self):
        logger = test.TestLogger(level='debug')
        logger.info('msg')
        self.assertEqual(logger.logged, [('info', 'msg')])

    def test_warning(self):
        logger = test.TestLogger(level='debug')
        logger.warning('msg')
        self.assertEqual(logger.logged, [('warning', 'msg')])

    def test_error(self):
        logger = test.TestLogger(level='debug')
        logger.error('msg')
        self.assertEqual(logger.logged, [('error', 'msg')])

    def test_exception(self):
        logger = test.TestLogger(level='debug')
        logger.exception('msg')
        self.assertEqual(logger.logged, [('exception', 'msg')])
