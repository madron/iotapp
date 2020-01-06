import asyncio
import logging
import os
import time
import aiofiles
import yaml
from . import constants


class ConfigManager(object):
    def __init__(self, config_dir='config', apps_dir='apps', queue=None, scan_wait=4, scan_interval=0.5):
        self.config_dir = config_dir
        self.apps_dir = apps_dir
        self.queue = queue or asyncio.Queue()
        self.monitor_queue = asyncio.Queue()
        self.stop_queue = asyncio.Queue()
        self.running = False
        self.monitor = ConfigMonitor(config_dir=config_dir, apps_dir=apps_dir, queue=self.monitor_queue, scan_wait=scan_wait, scan_interval=scan_interval)

    async def run(self):
        logging.info('ConfigManager started')
        self.running = True
        # Tasks
        self.tasks = asyncio.gather(
            asyncio.create_task(self.monitor.run()),
        )
        while True:
            try:
                await self.run_loop()
            except Exception:
                logging.exception('Unhandled exception in ConfigManager')
                await self.stop()
                return
        await self.tasks

    async def run_loop(self):
        await self.monitor_queue.get()
        await self.handle_config_change()
        self.monitor_queue.task_done()

    async def stop(self):
        if self.running:
            await self.monitor.stop()
            await self.monitor_queue.join()
            logging.info('ConfigManager stopped')
            self.running = False


    async def handle_config_change(self):
        devices_file_name = os.path.join(self.config_dir, constants.DEVICES_FILE_NAME)
        apps_file_name = os.path.join(self.config_dir, constants.APPS_FILE_NAME)
        async with aiofiles.open(devices_file_name, mode='r') as f:
            devices_file_content = await f.read()
        async with aiofiles.open(apps_file_name, mode='r') as f:
            apps_file_content = await f.read()
        devices = yaml.safe_load(devices_file_content)
        devices_ok, devices_ko = validate_devices(devices)
        for k, v in devices_ko.items():
            logging.error('Device "{}" discarded: {}'.format(k, v['error']))
        apps = yaml.safe_load(apps_file_content)
        apps_ok, apps_ko = validate_apps(devices_ok, apps)
        for k, v in apps_ko.items():
            logging.error('App "{}" discarded: {}'.format(k, v['error']))


class ConfigMonitor(object):
    def __init__(self, config_dir='config', apps_dir='apps', queue=None, scan_wait=2, scan_interval=1):
        self.config_dir = config_dir
        self.apps_dir = apps_dir
        self.queue = queue or asyncio.Queue()
        self.scan_wait = scan_wait
        self.scan_interval = scan_interval
        self.stop_queue = asyncio.Queue()
        self.next_scan_queues = []
        self.running = False
        self.config_files = dict()
        self.app_files = dict()

    async def run(self):
        logging.info('ConfigMonitor started')
        self.running = True
        loop = asyncio.get_running_loop()
        while self.stop_queue.empty():
            try:
                await self.run_loop(loop)
            except Exception:
                logging.exception('Unhandled exception in ConfigMonitor')
                await self.stop_queue.put('stop')
        await self.stop_queue.get()
        self.stop_queue.task_done()
        self.running = False

    async def run_loop(self, loop):
        config_files = await loop.run_in_executor(None, self.get_files, self.config_dir)
        app_files = await loop.run_in_executor(None, self.get_files, self.apps_dir)
        if not config_files == self.config_files or not app_files == self.app_files:
            self.config_files = config_files
            self.app_files = app_files
            await self.queue.put('change')
        # next_scan
        for scan_queue in self.next_scan_queues:
            await scan_queue.get()
            scan_queue.task_done()
        # wait loop
        for i in range(self.scan_wait):
            await asyncio.sleep(self.scan_interval)
            if not self.stop_queue.empty():
                break

    async def wait_next_scan(self):
        queue = asyncio.Queue()
        await queue.put(None)
        self.next_scan_queues.append(queue)
        await queue.join()
        self.next_scan_queues.remove(queue)

    async def stop(self):
        if self.running:
            await self.stop_queue.put('stop')
            await self.stop_queue.join()
            logging.info('ConfigMonitor stopped')

    def get_files(self, path):
        entries = os.scandir(path)
        return dict([(x.name, x.stat().st_mtime) for x in entries if x.is_file()])


def validate_devices(devices):
    ok = dict()
    ko = dict()
    for key, value in devices.items():
        error = validate_device(key, value)
        if error:
            ko[key] = dict(value=value, error=error)
        else:
            ok[key] = value
    devices = dict()
    errors = []
    for key, value in ok.items():
        for device_name in value.get('devices', dict()).keys():
            if device_name in devices:
                error = 'Duplicated device.'
                ko[key] = dict(value=value, error=error)
                errors.append(key)
            else:
                devices[device_name] = key
    for device_name in errors:
        del ok[device_name]
    return ok, ko


def validate_device(key, value):
    if 'type' not in value:
        return 'Missing type.'
    if not isinstance(value['type'], str):
        return 'Wrong type.'
    return None


def validate_apps(devices, apps):
    ok = dict()
    ko = dict()
    devices = get_device_dict(devices)
    for key, value in apps.items():
        value['devices'] = value.get('devices', [])
        error = validate_app(key, value, devices)
        if error:
            ko[key] = dict(value=value, error=error)
        else:
            ok[key] = value

    return ok, ko


def validate_app(app_name, app, devices):
    available_devices = list(devices.keys())
    if 'module' not in app:
        return 'Missing module.'
    if 'class' not in app:
        return 'Missing class.'
    for device in app['devices']:
        if device not in available_devices:
            return 'Device "{}" not available.'.format(device)
    return None


def get_device_dict(devices):
    device_dict = dict()
    for key, value in devices.items():
        for device in value.get('devices', dict()).keys():
            device_dict[device] = key
    return device_dict
