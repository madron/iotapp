import asyncio
import logging
import os
from . import config


class IotApp(object):
    def __init__(self, config_dir=None, apps_dir=None, mqtt_config=dict()):
        self.config_dir = config_dir
        self.apps_dir = apps_dir
        self.mqtt_config = mqtt_config
        self.tasks = None
        # queues
        self.config_queue = asyncio.Queue()

    async def run(self):
        logging.info('IotApp started')
        tasks = []
        # Config Manager
        self.config_manager = config.ConfigManager(config_dir=self.config_dir, apps_dir=self.apps_dir, queue=self.config_queue)
        tasks += [
            asyncio.create_task(self.config_manager.run()),
        ]
        # Gather tasks
        self.tasks = asyncio.gather(*tasks)
        await self.tasks

    async def stop(self):
        await self.config_manager.stop()
        if asyncio.isfuture(self.tasks):
            logging.info('Canceling tasks')
            self.tasks.cancel()
            logging.info('Waiting for tasks to finish')
            try:
                await self.tasks
            except asyncio.CancelledError:
                pass
            self.tasks = None
        queues = [
            self.config_queue,
        ]
        elements = sum([q.qsize() for q in queues])
        if elements:
            logging.info('Removing elements from queues: {}'.format(elements))
        for queue in queues:
            while queue.qsize():
                await queue.get()
                queue.task_done()
            await queue.join()
