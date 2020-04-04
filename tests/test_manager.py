import os
import unittest
from iotapp.apps.toggle import Toggle
from iotapp import entities
from iotapp.manager import AppManager
from iotapp.test import TestLogger


class AppManagerTest(unittest.TestCase):
    def setUp(self):
        self.logger = TestLogger()

    def test_file(self):
        devices = os.path.join(os.path.dirname(__file__), 'devices.yml')
        apps = os.path.join(os.path.dirname(__file__), 'apps.yml')
        manager = AppManager(name='toggle_kitchen_lamp', devices=devices, apps=apps)
        # App
        self.assertEqual(manager.app, 'iotapp.apps.toggle.Toggle')
        self.assertEqual(manager.config, dict(button='table_button', light='kitchen_lamp'))
        # Devices
        self.assertEqual(len(manager.entities), 2)
        # table_button
        entity = manager.entities['table_button']
        self.assertIsInstance(entity, entities.Button)
        self.assertEqual(entity.state_topic, 'zigbee/table_button')
        self.assertEqual(entity.state_value_click, 'single')
        # kitchen_lamp
        entity = manager.entities['kitchen_lamp']
        self.assertIsInstance(entity, entities.Light)
        self.assertEqual(entity.state_topic, 'shellies/kitchen_lamp/white/0')
        self.assertEqual(entity.command_topic, 'shellies/kitchen_lamp/white/0/command')
        # App Instance
        self.assertIsInstance(manager.app_instance, Toggle)

    def test_apps_entity_override(self):
        devices = dict(
            button=dict(type='aqara-button'),
            light=dict(type='shelly-rgbw2'),
        )
        apps = dict(
            app=dict(
                app='iotapp.apps.toggle.Toggle',
                entities=dict(
                    button=dict(log_level='debug'),
                ),
                button='button',
                light='light',
            ),
        )
        manager = AppManager(name='app', devices=devices, apps=apps)
        # button
        entity = manager.entities['button']
        self.assertEqual(entity.log_level, 'debug')