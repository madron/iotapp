import os
import unittest
from iotapp import entities
from iotapp.config import DeviceManager
from iotapp.config import get_entities, validate_devices, validate_apps
from iotapp.test import TestLogger


class DevicesManagerTest(unittest.TestCase):
    def setUp(self):
        self.logger = TestLogger()

    def test_entities(self):
        devices = dict(
            button=dict(
                type='aqara-button',
            ),
            kitchen=dict(
                type='shelly-rgbw2',
                mode='white',
            ),
        )
        manager = DeviceManager(devices=devices)
        # entities
        self.assertEqual(len(manager.entities), 2)
        # button
        entity = manager.entities['button']
        self.assertEqual(entity['class'], entities.Button)
        config = entity['config']
        self.assertEqual(config['state_topic'], 'zigbee/button')
        self.assertEqual(config['state_value_click'], 'single')
        self.assertEqual(config['state_template'], '{{ value.click }}')
        # kitchen
        entity = manager.entities['kitchen']
        self.assertEqual(entity['class'], entities.Light)
        config = entity['config']
        self.assertEqual(config['state_topic'], 'shellies/kitchen/white/0')
        self.assertEqual(config['command_topic'], 'shellies/kitchen/white/0/command')

    def test_wrong_config(self):
        devices = dict(
            button=dict(
                type='aqara-button',
                wrong=True,
            ),
            kitchen=dict(
                type='shelly-rgbw2',
                mode='white',
            ),
        )
        manager = DeviceManager(devices=devices, logger=self.logger)
        self.assertEqual(len(manager.entities), 1)
        self.assertEqual(self.logger.logged, [('exception', 'device discarded: button')])
        # kitchen
        entity = manager.entities['kitchen']
        self.assertEqual(entity['class'], entities.Light)
        config = entity['config']
        self.assertEqual(config['state_topic'], 'shellies/kitchen/white/0')
        self.assertEqual(config['command_topic'], 'shellies/kitchen/white/0/command')


class ValidateDevicesTest(unittest.TestCase):
    def test_ok(self):
        devices = dict(kitchen=dict(type='tasmota-sonoff'))
        ok, ko = validate_devices(devices)
        self.assertEqual(ok, dict(kitchen=dict(type='tasmota-sonoff')))
        self.assertEqual(ko, dict())

    def test_empty(self):
        devices = dict()
        ok, ko = validate_devices(devices)
        self.assertEqual(ok, dict())
        self.assertEqual(ko, dict())

    def test_missing_type(self):
        devices = dict(kitchen=dict())
        ok, ko = validate_devices(devices)
        self.assertEqual(ok, dict())
        device = 'kitchen'
        value = ko[device]['value']
        error = ko[device]['error']
        self.assertEqual(value, dict())
        self.assertEqual(error, 'Missing type.')

    def test_type_wrong_type(self):
        devices = dict(kitchen=dict(type=1))
        ok, ko = validate_devices(devices)
        self.assertEqual(ok, dict())
        device = 'kitchen'
        value = ko[device]['value']
        error = ko[device]['error']
        self.assertEqual(value, dict(type=1))
        self.assertEqual(error, 'Wrong type.')

    def test_duplicated_entities(self):
        devices = dict(
            kitchen=dict(type='tasmota', entities=dict(lamp1=1)),
            bedroom=dict(type='shelly', entities=dict(lamp1=2)),
        )
        ok, ko = validate_devices(devices)
        self.assertEqual(ok, dict(kitchen=dict(type='tasmota', entities=dict(lamp1=1))))
        device = 'bedroom'
        value = ko[device]['value']
        error = ko[device]['error']
        self.assertEqual(value, dict(type='shelly', entities=dict(lamp1=2)))
        self.assertEqual(error, 'Duplicated entity.')


class GetEntitiesTest(unittest.TestCase):
    def test_ok(self):
        devices = dict(
            kitchen=dict(type='tasmota-shelly-2.5', entities=dict(kitchen_lamp=1, coffee_machine=2)),
            living_room=dict(type='tasmota-sonoff', entities=dict(living_room_lamp=1, tv=2)),
        )
        entities = get_entities(devices)
        self.assertEqual(len(entities), 4)
        self.assertEqual(entities['kitchen_lamp'], 'kitchen')
        self.assertEqual(entities['coffee_machine'], 'kitchen')
        self.assertEqual(entities['living_room_lamp'], 'living_room')
        self.assertEqual(entities['tv'], 'living_room')


class ValidateAppsTest(unittest.TestCase):
    def test_ok(self):
        devices = dict(kitchen=dict(type='tasmota-sonoff', entities=dict(kitchen_lamp=1)))
        apps = {'switch_lamp': {'module': 'toggle', 'class': 'Toggle', 'entities': ['kitchen_lamp']}}
        ok, ko = validate_apps(devices, apps)
        self.assertEqual(ok, {'switch_lamp': {'module': 'toggle', 'class': 'Toggle', 'entities': ['kitchen_lamp']}})
        self.assertEqual(ko, dict())

    def test_missing_device_parameter(self):
        devices = dict(kitchen=dict(type='tasmota-sonoff', entities=dict(kitchen_lamp=1)))
        apps = {'switch_lamp': {'module': 'toggle', 'class': 'Toggle'}}
        ok, ko = validate_apps(devices, apps)
        self.assertEqual(ok, {'switch_lamp': {'module': 'toggle', 'class': 'Toggle', 'entities': []}})
        self.assertEqual(ko, dict())

    def test_missing_module(self):
        devices = dict(kitchen=dict(type='tasmota-sonoff', entities=dict(kitchen_lamp=1)))
        apps = {'switch_lamp': {'class': 'Toggle', 'entities': ['kitchen_lamp']}}
        ok, ko = validate_apps(devices, apps)
        self.assertEqual(ok, dict())
        app = 'switch_lamp'
        value = ko[app]['value']
        error = ko[app]['error']
        self.assertEqual(value, {'class': 'Toggle', 'entities': ['kitchen_lamp']})
        self.assertEqual(error, 'Missing module.')

    def test_missing_class(self):
        devices = dict(kitchen=dict(type='tasmota-sonoff', entities=dict(kitchen_lamp=1)))
        apps = {'switch_lamp': {'module': 'toggle', 'entities': ['kitchen_lamp']}}
        ok, ko = validate_apps(devices, apps)
        self.assertEqual(ok, dict())
        app = 'switch_lamp'
        value = ko[app]['value']
        error = ko[app]['error']
        self.assertEqual(value, {'module': 'toggle', 'entities': ['kitchen_lamp']})
        self.assertEqual(error, 'Missing class.')

    def test_missing_device(self):
        devices = dict(kitchen=dict(type='tasmota-sonoff', entities=dict(kitchen_lamp=1)))
        apps = {'switch_lamp': {'module': 'toggle', 'class': 'Toggle', 'entities': ['tv']}}
        ok, ko = validate_apps(devices, apps)
        self.assertEqual(ok, dict())
        app = 'switch_lamp'
        value = ko[app]['value']
        error = ko[app]['error']
        self.assertEqual(value, {'module': 'toggle', 'class': 'Toggle', 'entities': ['tv']})
        self.assertEqual(error, 'Entity "tv" not available.')

    def test_empty(self):
        devices = dict(kitchen=dict(type='tasmota-sonoff', entities=dict(kitchen_lamp=1)))
        apps = dict()
        ok, ko = validate_apps(devices, apps)
        self.assertEqual(ok, dict())
        self.assertEqual(ko, dict())
