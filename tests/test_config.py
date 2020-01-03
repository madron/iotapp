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
