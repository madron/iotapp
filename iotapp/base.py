import os
import logging
import sys
import paho.mqtt.client as mqtt


class LoggerMixin:
    def get_logger(self, level=None, name=__name__):
        log_level = dict(
            debug=logging.DEBUG,
            info=logging.INFO,
            warning=logging.WARNING,
            error=logging.ERROR,
        )
        level = level or getattr(self, 'log_level', None) or os.environ.get('LOG_LEVEL', 'info')
        logger = logging.getLogger(name)
        logger.setLevel(log_level[level])
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(levelname)-8s %(name)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger


class IotApp(LoggerMixin):
    entities = dict()

    def __init__(self, log_level=None, client=None, logger=None):
        self.logger = logger or self.get_logger(level=log_level, name='app')
        self.mqtt_config = self.get_mqtt_config()
        self.client = client or mqtt.Client(client_id=self.mqtt_config['client_id'])
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.topic_entity = dict()
        # Entities
        for name, entity_class in self.entities.items():
            entity = entity_class(name=name, client=self.client)
            setattr(self, name, entity)
            # entiry
            for topic in entity.get_event_topics():
                self.client.subscribe(topic)
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
        try:
            self.logger.info('Connected to {host}:{port}'.format(**self.mqtt_config))
            for topic, entity_name in self.topic_entity.items():
                entity = getattr(self, entity_name)
                for topic in entity.get_event_topics():
                    self.client.subscribe(topic)
                entity.on_connect()
        except:
            self.logger.exception('on_connect', exc_info=True)

    def on_message(self, client, userdata, msg):
        try:
            self.logger.debug('on_message - {} {}'.format(msg.topic, msg.payload))
            entity_name = self.topic_entity[msg.topic]
            entity = getattr(self, entity_name)
            event = entity.get_event(msg.topic, msg.payload.decode('utf-8'))
            if event:
                self.on_event(event, entity_name)
        except:
            msg = 'on_message - topic: {} - payload: {} - userdata: {}'.format(msg.topic, msg.payload, userdata)
            self.logger.exception(msg, exc_info=True)

    def on_event(self, event, name):
        try:
            self.logger.debug('on_event - event: {} - name: {}'.format(event, name))
            func_name = 'on_{}_{}'.format(name, event['type'])
            func = getattr(self, func_name, None)
            if func:
                try:
                    func()
                except:
                    msg = '{} - event: {}'.format(func_name, event)
                    self.logger.exception(msg, exc_info=True)
        except:
            msg = 'on_event - event: {} - name: {}'.format(event, name)
            self.logger.exception(msg, exc_info=True)

    def run(self):
        self.client.connect(
            self.mqtt_config['host'],
            self.mqtt_config['port'],
            self.mqtt_config['keepalive'],
        )
        self.client.loop_forever()
