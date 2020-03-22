import asyncio
import os
import tempfile
import unittest
import aiofiles
from iotapp import config


class ConfigMonitorTest(unittest.IsolatedAsyncioTestCase):
    async def test_change(self):
        with tempfile.TemporaryDirectory() as config_dir:
            with tempfile.TemporaryDirectory() as apps_dir:
                queue = asyncio.Queue()
                config_monitor = config.ConfigMonitor(config_dir=config_dir, apps_dir=apps_dir, queue=queue, scan_wait=1, scan_interval=0.01)
                task = asyncio.create_task(config_monitor.run())
                self.assertTrue(queue.empty())
                # add config file
                file_name = os.path.join(config_dir, 'file.txt')
                f = await aiofiles.open(file_name, mode='w')
                await f.close()
                await config_monitor.wait_next_scan()
                self.assertFalse(queue.empty())
                event = await queue.get()
                self.assertEqual(event, 'change')
                # add app file
                file_name = os.path.join(apps_dir, 'file.txt')
                f = await aiofiles.open(file_name, mode='w')
                await f.close()
                await config_monitor.wait_next_scan()
                self.assertFalse(queue.empty())
                event = await queue.get()
                self.assertEqual(event, 'change')
                # add config and apps file
                file_name = os.path.join(config_dir, 'anotherfile.txt')
                f = await aiofiles.open(file_name, mode='w')
                await f.close()
                file_name = os.path.join(apps_dir, 'anotherfile.txt')
                f = await aiofiles.open(file_name, mode='w')
                await f.close()
                await config_monitor.wait_next_scan()
                self.assertEqual(queue.qsize(), 1)
                event = await queue.get()
                self.assertEqual(event, 'change')
                # Stop monitor
                await config_monitor.stop()


class ValidateDevicesTest(unittest.TestCase):
    def test_ok(self):
        devices = dict(kitchen=dict(type='tasmota-sonoff'))
        ok, ko = config.validate_devices(devices)
        self.assertEqual(ok, dict(kitchen=dict(type='tasmota-sonoff')))
        self.assertEqual(ko, dict())

    def test_empty(self):
        devices = dict()
        ok, ko = config.validate_devices(devices)
        self.assertEqual(ok, dict())
        self.assertEqual(ko, dict())

    def test_missing_type(self):
        devices = dict(kitchen=dict())
        ok, ko = config.validate_devices(devices)
        self.assertEqual(ok, dict())
        device = 'kitchen'
        value = ko[device]['value']
        error = ko[device]['error']
        self.assertEqual(value, dict())
        self.assertEqual(error, 'Missing type.')

    def test_type_wrong_type(self):
        devices = dict(kitchen=dict(type=1))
        ok, ko = config.validate_devices(devices)
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
        ok, ko = config.validate_devices(devices)
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
        entities = config.get_entities(devices)
        self.assertEqual(len(entities), 4)
        self.assertEqual(entities['kitchen_lamp'], 'kitchen')
        self.assertEqual(entities['coffee_machine'], 'kitchen')
        self.assertEqual(entities['living_room_lamp'], 'living_room')
        self.assertEqual(entities['tv'], 'living_room')


class ValidateAppsTest(unittest.TestCase):
    def test_ok(self):
        devices = dict(kitchen=dict(type='tasmota-sonoff', entities=dict(kitchen_lamp=1)))
        apps = {'switch_lamp': {'module': 'toggle', 'class': 'Toggle', 'entities': ['kitchen_lamp']}}
        ok, ko = config.validate_apps(devices, apps)
        self.assertEqual(ok, {'switch_lamp': {'module': 'toggle', 'class': 'Toggle', 'entities': ['kitchen_lamp']}})
        self.assertEqual(ko, dict())

    def test_missing_device_parameter(self):
        devices = dict(kitchen=dict(type='tasmota-sonoff', entities=dict(kitchen_lamp=1)))
        apps = {'switch_lamp': {'module': 'toggle', 'class': 'Toggle'}}
        ok, ko = config.validate_apps(devices, apps)
        self.assertEqual(ok, {'switch_lamp': {'module': 'toggle', 'class': 'Toggle', 'entities': []}})
        self.assertEqual(ko, dict())

    def test_missing_module(self):
        devices = dict(kitchen=dict(type='tasmota-sonoff', entities=dict(kitchen_lamp=1)))
        apps = {'switch_lamp': {'class': 'Toggle', 'entities': ['kitchen_lamp']}}
        ok, ko = config.validate_apps(devices, apps)
        self.assertEqual(ok, dict())
        app = 'switch_lamp'
        value = ko[app]['value']
        error = ko[app]['error']
        self.assertEqual(value, {'class': 'Toggle', 'entities': ['kitchen_lamp']})
        self.assertEqual(error, 'Missing module.')

    def test_missing_class(self):
        devices = dict(kitchen=dict(type='tasmota-sonoff', entities=dict(kitchen_lamp=1)))
        apps = {'switch_lamp': {'module': 'toggle', 'entities': ['kitchen_lamp']}}
        ok, ko = config.validate_apps(devices, apps)
        self.assertEqual(ok, dict())
        app = 'switch_lamp'
        value = ko[app]['value']
        error = ko[app]['error']
        self.assertEqual(value, {'module': 'toggle', 'entities': ['kitchen_lamp']})
        self.assertEqual(error, 'Missing class.')

    def test_missing_device(self):
        devices = dict(kitchen=dict(type='tasmota-sonoff', entities=dict(kitchen_lamp=1)))
        apps = {'switch_lamp': {'module': 'toggle', 'class': 'Toggle', 'entities': ['tv']}}
        ok, ko = config.validate_apps(devices, apps)
        self.assertEqual(ok, dict())
        app = 'switch_lamp'
        value = ko[app]['value']
        error = ko[app]['error']
        self.assertEqual(value, {'module': 'toggle', 'class': 'Toggle', 'entities': ['tv']})
        self.assertEqual(error, 'Entity "tv" not available.')

    def test_empty(self):
        devices = dict(kitchen=dict(type='tasmota-sonoff', entities=dict(kitchen_lamp=1)))
        apps = dict()
        ok, ko = config.validate_apps(devices, apps)
        self.assertEqual(ok, dict())
        self.assertEqual(ko, dict())
