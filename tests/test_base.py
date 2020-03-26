import unittest
from iotapp.base import IotApp
from iotapp.test import TestClient, TestLogger


class IotAppTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient()
        self.logger = TestLogger()

    def test_init(self):
        IotApp(client=self.client, logger=self.logger)

    def test_connect(self):
        IotApp(client=self.client, logger=self.logger)
        self.client.connect()
        self.assertEqual(self.logger.logged, [('info', 'Connected to localhost:1883')])

    def test_publish(self):
        self.client.publish('topic', payload='data')
        self.assertEqual(self.client.published, [('topic', 'data')])

    def test_subscribe(self):
        IotApp(client=self.client, logger=self.logger)
        self.client.subscribe('topic')
        self.assertEqual(self.client.subscribed, ['topic'])

    def test_receive(self):
        self.logger = TestLogger(level='debug')
        IotApp(client=self.client, logger=self.logger)
        self.client.receive('topic', 'data')
        self.assertEqual(self.logger.logged[0], ('debug', "on_message - topic b'data'"))
