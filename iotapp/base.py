import os
import paho.mqtt.client as mqtt
from copy import copy
from iotapp.config import DeviceManager
from iotapp.logger import LoggerMixin


class IotApp(LoggerMixin):
    entities = dict()

    def __init__(self, name=None, entity_library=dict(), availability_topic=None, log_level=None, client=None, logger=None):
        self.name = name or type(self).__name__.lower()
        self.entity_library = entity_library
        self.availability_topic = availability_topic or 'iotapp/{}/state'.format(self.name)
        self.logger = logger or self.get_logger(level=log_level)
        self.mqtt_config = self.get_mqtt_config()
        self.client = client or mqtt.Client(client_id=self.mqtt_config['client_id'])
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.topic_entity = dict()

    def add_entity(self, name, entity_name):
        entity = copy(self.entity_library[entity_name])
        entity.set_name(name=name)
        entity.set_client(self.client)
        entity.set_logger(name=name)
        entity.reset_state()
        setattr(self, name, entity)
        for topic in entity.get_subscribe_topics():
            self.topic_entity[topic] = name

    def get_mqtt_config(self):
        username = os.environ.get('MQTT_USERNAME', None)
        return dict(
            host=os.environ.get('MQTT_HOST', 'localhost'),
            port=int(os.environ.get('MQTT_PORT', 1883)),
            keepalive=int(os.environ.get('MQTT_KEEPALIVE', 10)),
            username=os.environ.get('MQTT_USERNAME', None),
            password=os.environ.get('MQTT_PASSWORD', None),
            client_id=os.environ.get('MQTT_CLIENT_ID', None)
        )

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            try:
                self.logger.info('Connected to {host}:{port}'.format(**self.mqtt_config))
                self.client.will_set(self.availability_topic, 'offline', retain=True)
                self.client.publish(self.availability_topic, 'online', retain=True)
                for topic, entity_name in self.topic_entity.items():
                    entity = getattr(self, entity_name)
                    for topic in entity.get_subscribe_topics():
                        self.client.subscribe(topic)
                    try:
                        entity.on_connect()
                    except:
                        self.logger.exception('on_connect {}'.format(entity_name), exc_info=True)
                        raise
            except:
                self.logger.exception('on_connect', exc_info=True)
        else:
            msg = mqtt.error_string(rc)
            self.logger.error('Could not connect to {host}:{port} - Return code {} ({})'.format(rc, msg, **self.mqtt_config))

    def on_message(self, client, userdata, msg):
        try:
            self.logger.debug('on_message - {} {}'.format(msg.topic, msg.payload))
            entity_name = self.topic_entity[msg.topic]
            entity = getattr(self, entity_name)
            events = entity.get_events(msg.topic, msg.payload.decode('utf-8'))
            for event in events:
                self.process_event(entity_name, event)
        except:
            msg = 'on_message - topic: {} - payload: {} - userdata: {}'.format(msg.topic, msg.payload, userdata)
            self.logger.exception(msg, exc_info=True)

    def process_event(self, name, event):
        self.logger.debug('process_event - {} {}'.format(name, event))
        func_name = 'on_{}_{}'.format(name, event.type)
        func = getattr(self, func_name, None)
        if func:
            try:
                func(*event.args, **event.kwargs)
            except:
                msg = '{} - event: {}'.format(func_name, event)
                self.logger.exception(msg, exc_info=True)
