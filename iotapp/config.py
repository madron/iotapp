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
            await self.monitor_queue.get()
            await self.handle_config_change()
            self.monitor_queue.task_done()
        await self.tasks

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
        apps = yaml.safe_load(apps_file_content)


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
        await self.stop_queue.get()
        self.stop_queue.task_done()
        self.running = False

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
