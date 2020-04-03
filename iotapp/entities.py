import json
from jinja2 import Template
from iotapp.events import Event
from iotapp.logger import LoggerMixin


class Entity(LoggerMixin):
    def __init__(
                    self,
                    name=None,
                    client=None,
                    logger=None,
                    log_level=None,
                    availability_topic=None,
                    availability_online='online',
                    availability_offline='offline',
                ):
        self.set_name(name)
        self.set_client(client)
        self.log_level = log_level
        self.logger = logger or self.get_logger(name='entity')
        self.availability_topic = availability_topic
        self.availability_online = availability_online
        self.availability_offline = availability_offline
        self.reset_state()

    def reset_state(self):
        self.available = None

    def set_name(self, name):
        self.name = name

    def set_client(self, client):
        self.client = client

    def get_subscribe_topics(self):
        topics = []
        if self.availability_topic:
            topics.append(self.availability_topic)
        return topics

    def get_events(self, topic, payload):
        self.logger.debug('get_events - {} {}'.format(topic, payload))
        events = []
        if topic == self.availability_topic:
            value = None
            if payload == self.availability_online:
                value = True
            elif payload == self.availability_offline:
                value = False
            if not value == self.available:
                if value:
                    events.append(Event('availability', 'online'))
                    self.available = True
                    self.logger.info('Status online')
                else:
                    events.append(Event('availability', 'offline'))
                    self.available = False
                    self.logger.warning('Status offline')
        return events

    def on_connect(self):
        pass


class StateEntity(Entity):
    def __init__(   self,
                    state_topic=None,
                    state_type='text',
                    state_value_template='',
                    **kwargs,
                ):
        super().__init__(**kwargs)
        self.state_topic = state_topic
        self.state_type = state_type
        self.state_value_template = Template(state_value_template)
        self.reset_state()

    def reset_state(self):
        super().reset_state()
        self.state = None

    def get_subscribe_topics(self):
        topics = super().get_subscribe_topics()
        if self.state_topic:
            topics.append(self.state_topic)
        return topics

    def get_events(self, topic, payload):
        events = super().get_events(topic, payload)
        if topic == self.state_topic:
            value = None
            if self.state_type == 'text':
                value = payload
            elif self.state_type == 'json':
                data = json.loads(payload)
                value = self.state_value_template.render(value=data)
            events += self.get_state_events(value)
        return events

    def get_state_events(self, value):
        return []


class Button(StateEntity):
    def __init__(   self,
                    state_value_click='click',
                    **kwargs,
                ):
        super().__init__(**kwargs)
        self.state_value_click = state_value_click

    def get_state_events(self, value):
        events = super().get_state_events(value)
        if value == self.state_value_click:
            events.append(Event('click'))
        return events


class Light(StateEntity):
    def __init__(   self,
                    state_value_on='on',
                    state_value_off='off',
                    #
                    command_topic=None,
                    command_type='text',
                    command_value_on='on',
                    command_value_off='off',
                    command_value_template='',
                    **kwargs
                ):
        super().__init__(**kwargs)
        self.state_value_on = state_value_on
        self.state_value_off = state_value_off
        self.command_topic = command_topic
        self.command_type = command_type
        self.command_value_on = command_value_on
        self.command_value_off = command_value_off
        self.command_value_template = command_value_template

    def get_state_events(self, value):
        events = super().get_state_events(value)
        if value == self.state_value_on:
            self.state = 'on'
        elif value == self.state_value_off:
            self.state = 'off'
        return events

    def turn_on(self):
        self.client.publish(self.command_topic, payload=self.command_value_on)
        self.logger.debug('turn_on')

    def turn_off(self):
        self.client.publish(self.command_topic, payload=self.command_value_off)
        self.logger.debug('turn_off')

    def toggle(self):
        self.logger.debug('toggle - state: {}'.format(self.state))
        if self.state == 'on':
            self.turn_off()
            return 'off'
        elif self.state == 'off':
            self.turn_on()
            return 'on'
        self.logger.warning('toggle - state not available')
