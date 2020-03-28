import unittest
from iotapp import devices
from iotapp.base import IotApp
from iotapp.events import Event
from iotapp.test import TestClient, TestLogger


class ToggleApp(IotApp):
    log_level = 'debug'
    entities = dict(
        button=devices.Button(state_topic='button/state'),
        light=devices.Light(state_topic='light/state', command_topic='light/command'),
    )

    def on_button_click(self):
        state = self.light.toggle()
        self.logger.info('on_button_click -> light: {}'.format(state))


class ToggleTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient()
        self.logger = TestLogger()
        self.app = ToggleApp(client=self.client, logger=self.logger)
        self.app.button.logger = self.logger
        self.app.light.logger = self.logger

    def test_connect(self):
        self.client.connect()
        self.assertEqual(self.logger.logged, [('info', 'Connected to localhost:1883')])
        self.assertEqual(self.client.subscribed, ['button/state', 'light/state'])

    def test_button_state_on_low_level(self):
        # Light state on
        self.client.receive('light/state', 'on')
        self.assertEqual(self.app.light.state, 'on')
        # Button pressed
        self.client.receive('button/state', 'click')
        self.assertEqual(self.client.published, [('light/command', 'off')])
        self.assertEqual(self.logger.logged, [('info', 'on_button_click -> light: off')])

    def test_button_state_on(self):
        # Light state on
        self.app.light.state = 'on'
        # Button pressed
        self.app.process_event('button', Event('click'))
        self.assertEqual(self.logger.logged, [('info', 'on_button_click -> light: off')])

    def test_button_state_off(self):
        # Light state off
        self.client.receive('light/state', 'off')
        self.assertEqual(self.app.light.state, 'off')
        # Button pressed
        self.client.receive('button/state', 'click')
        self.assertEqual(self.client.published, [('light/command', 'on')])
        self.assertEqual(self.logger.logged, [('info', 'on_button_click -> light: on')])

    def test_button_state_unknown(self):
        # Light state
        self.assertEqual(self.app.light.state, None)
        # Button pressed
        self.client.receive('button/state', 'click')
        self.assertEqual(self.client.published, [])
        self.assertEqual(self.logger.logged[0], ('warning', 'toggle - state not available'))
        self.assertEqual(self.logger.logged[1], ('info', 'on_button_click -> light: None'))
