import unittest
from iotapp import entities
from iotapp.apps.toggle import Toggle
from iotapp.base import IotApp
from iotapp.events import Event
from iotapp.test import TestClient, TestLogger


class ToggleTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient()
        self.logger = TestLogger()
        entity_library = dict(
            button=entities.Button(),
            light=entities.Light(),
        )
        self.app = Toggle(entity_library=entity_library, button='button', light='light', client=self.client, logger=self.logger)
        self.app.button.logger = self.logger
        self.app.light.logger = self.logger

    def test_button_state_on(self):
        # Light state on
        self.app.light.state = 'on'
        # Button pressed
        self.app.process_event('button', Event('click'))
        self.assertEqual(self.logger.logged, [('info', 'on_button_click -> light: off')])

    def test_button_state_off(self):
        # Light state off
        self.app.light.state = 'off'
        # Button pressed
        self.app.process_event('button', Event('click'))
        self.assertEqual(self.logger.logged, [('info', 'on_button_click -> light: on')])

    def test_button_state_unknown(self):
        # Light state
        self.assertEqual(self.app.light.state, None)
        # Button pressed
        self.app.process_event('button', Event('click'))
        self.assertEqual(self.logger.logged[0], ('warning', 'toggle - state not available'))
        self.assertEqual(self.logger.logged[1], ('info', 'on_button_click -> light: None'))
