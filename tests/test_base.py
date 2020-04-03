import unittest
from iotapp import entities
from iotapp.base import IotApp
from iotapp.test import TestClient, TestLogger


class IotAppTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient()
        self.logger = TestLogger()

    def test_init(self):
        IotApp(client=self.client, logger=self.logger)

    def test_connect(self):
        IotApp(availability_topic='iotapp/app/state', client=self.client, logger=self.logger)
        self.client.connect()
        self.assertEqual(self.logger.logged, [('info', 'Connected to localhost:1883')])
        self.assertEqual(self.client.will_set_called, [('iotapp/app/state', 'offline')])
        self.assertEqual(self.client.published, [('iotapp/app/state', 'online')])

    def test_connect_fail(self):
        IotApp(availability_topic='iotapp/app/state', client=self.client, logger=self.logger)
        self.client.connect(rc=5)
        self.assertEqual(self.logger.logged, [('error', 'Could not connect to localhost:1883 - Return code 5 (The connection was refused.)')])
        self.assertEqual(self.client.will_set_called, [])
        self.assertEqual(self.client.published, [])

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

    def test_add_entity(self):
        self.logger = TestLogger(level='debug')
        app = IotApp(entity_library=dict(table_button=entities.Button()), client=self.client, logger=self.logger)
        app.add_entity('button', 'table_button')
        self.assertIsInstance(app.button, entities.Button)
        self.assertEqual(app.button.name, 'button')
