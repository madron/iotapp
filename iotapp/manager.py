import os
import yaml
from copy import copy
from importlib import import_module
from iotapp.config import DeviceManager
from iotapp.logger import LoggerMixin


class AppManager(LoggerMixin):
    def __init__(self, name=None, devices='', apps='', log_level=None, logger=None):
        self.logger = logger or self.get_logger(name='app_manager', level=log_level)
        # App name
        self.name = name or os.environ.get('IOTAPP_NAME')
        # Devices
        if isinstance(devices, str):
            file_name = devices or os.environ.get('IOTAPP_DEVICES', 'devices.yml')
            devices_file = open(file_name, 'r')
            self.devices = yaml.safe_load(devices_file)
            devices_file.close()
        else:
            self.devices = copy(devices)
        # Apps
        if isinstance(apps, str):
            file_name = apps or os.environ.get('IOTAPP_APPS')
            apps_file = open(file_name, 'r')
            self.apps = yaml.safe_load(apps_file)
            apps_file.close()
        else:
            self.apps = copy(apps)
        # Config
        app_data = copy(self.apps[self.name])
        self.app = app_data.pop('app')
        self.entity_config = app_data.pop('entities', dict())
        self.config = app_data
        # Entities
        device_manager = DeviceManager(devices=self.devices, log_level=log_level, logger=logger)
        self.entities = dict()
        for entity_name, entity_data in device_manager.entities.items():
            entity_class = entity_data['class']
            entity_config = entity_data['config']
            self.entities[entity_name] = entity_class(**entity_config)
        # App instance
        self.app_class = self.get_app_class()
        self.app_instance = self.app_class(name=self.name, entity_library=self.entities,  **self.config)

    def get_app_class(self):
        parts = self.app.split('.')
        module_name = '.'.join(parts[0:-1])
        class_name = parts[-1]
        module = import_module(module_name)
        return getattr(module, class_name)

    def run(self):
        self.app_instance.client.connect(
            self.app_instance.mqtt_config['host'],
            self.app_instance.mqtt_config['port'],
            self.app_instance.mqtt_config['keepalive'],
        )
        self.app_instance.client.loop_forever()
